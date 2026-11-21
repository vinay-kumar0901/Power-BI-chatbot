from pathlib import Path
import json, shutil, zipfile, uuid, re, threading
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from .config import ROOT, DASHBOARDS, UPLOADS
from . import store
from .powerbi import extract_dashboard
from .datasets import import_files, db_path, schema_for
from .rag import DashboardRAG
from .sql_agent import propose_sql, execute_readonly
from .llm import answer as llm_answer

app=FastAPI(title='BI-GPT Advanced',version='3.8.0')
CACHE={}
CHAT_EXECUTOR=ThreadPoolExecutor(max_workers=2)
CHAT_JOBS={}
CHAT_JOBS_LOCK=threading.Lock()
class ChatRequest(BaseModel): chat_id:str; question:str; dashboard:str|None=None
class NewChat(BaseModel): dashboard:str|None=None

def dashboard_names():
    return sorted([p.name for p in DASHBOARDS.iterdir() if p.is_dir() and not p.name.startswith('.')])
def safe_dashboard(name):
    if not name or name not in dashboard_names(): raise HTTPException(404,'Dashboard not found. Upload or add a Power BI project folder first.')
    return name
def load_dashboard(name):
    safe_dashboard(name)
    if name in CACHE:return CACHE[name]
    folder=DASHBOARDS/name
    # Permit a dashboard root folder containing the PBIP directly or a nested project folder.
    candidates=list(folder.rglob('*.pbip'))
    project=candidates[0].parent if candidates else folder
    summary,docs=extract_dashboard(project)
    # Add knowledge markdown documents as RAG source.
    for f in (ROOT/'knowledge').glob('*.md'):
        docs.append({'source':f'knowledge/{f.name}','text':f.read_text(encoding='utf-8',errors='ignore')})
    docs.append({'source':'Power BI model summary','text':json.dumps(summary,ensure_ascii=False,indent=2)})
    schema=schema_for(db_path(name))
    docs.append({'source':'SQL database schema','text':schema})
    CACHE[name]={'summary':summary,'docs':docs,'rag':None,'project':str(project)}
    return CACHE[name]

def history_text(cid,limit=12):
    data=store.get_chat(cid); return '\n'.join(f"{m['role']}: {m['content']}" for m in (data or {}).get('messages',[])[-limit:])

@app.on_event('startup')
def startup():
    # Keep startup fast and reliable. Dashboard metadata and embeddings are loaded lazily.
    store.init_store()

@app.get('/',response_class=HTMLResponse)
def home(): return (ROOT/'app'/'index.html').read_text(encoding='utf-8')
@app.get('/api/dashboards')
def dashboards():
    # Do not run PBIP parsing or Ollama embedding while the browser loads the dashboard selector.
    return [{'name': n} for n in dashboard_names()]
@app.post('/api/chats')
def new_chat(body:NewChat):
    d=body.dashboard
    if d: safe_dashboard(d)
    cid=store.create_chat(d); return {'id':cid,'title':'New chat','dashboard':d}
@app.get('/api/chats')
def chats(): return store.list_chats()
@app.get('/api/chats/{cid}')
def get_chat(cid):
    item=store.get_chat(cid)
    if not item: raise HTTPException(404,'Chat not found')
    return item
@app.delete('/api/chats/{cid}')
def remove_chat(cid): store.delete_chat(cid); return {'ok':True}
@app.post('/api/upload')
async def upload_dashboard(file:UploadFile=File(...), dashboard_name:str=Form('')):
    if not file.filename.lower().endswith('.zip'): raise HTTPException(400,'Upload a ZIP containing the Power BI project folder and optional CSV/XLSX exports.')
    name=re.sub(r'[^A-Za-z0-9 _-]','',dashboard_name.strip())[:60] or Path(file.filename).stem
    name=name.strip() or 'Dashboard'
    target=DASHBOARDS/name
    if target.exists(): name=f'{name}_{uuid.uuid4().hex[:5]}'; target=DASHBOARDS/name
    temp=UPLOADS/f'{uuid.uuid4().hex}.zip'
    with temp.open('wb') as f: shutil.copyfileobj(file.file,f)
    try:
        with zipfile.ZipFile(temp) as z:
            for info in z.infolist():
                dest=(target/info.filename).resolve()
                if target.resolve() not in dest.parents and dest!=target.resolve(): raise HTTPException(400,'Unsafe ZIP path detected.')
            z.extractall(target)
    except zipfile.BadZipFile: raise HTTPException(400,'The uploaded file is not a valid ZIP.')
    finally: temp.unlink(missing_ok=True)
    # Find the folder containing the PBIP and normalize it to dashboard root.
    pbips=list(target.rglob('*.pbip'))
    if not pbips: shutil.rmtree(target,ignore_errors=True); raise HTTPException(400,'ZIP must contain a .pbip file and its sibling Report/SemanticModel folders.')
    project=pbips[0].parent
    # data/ or datasets/ within zip are copied to a per-dashboard data directory
    data_target=ROOT/'data'/name; data_target.mkdir(parents=True,exist_ok=True)
    for folder in list(target.rglob('data'))+list(target.rglob('datasets')):
        if folder.is_dir():
            for f in folder.rglob('*'):
                if f.is_file() and f.suffix.lower() in {'.csv','.xlsx','.xls'}: shutil.copy2(f,data_target/f.name)
    # also import exports located beside the PBIP under Data/Exports
    for f in target.rglob('*'):
        if f.is_file() and f.suffix.lower() in {'.csv','.xlsx','.xls'} and f.parent!=data_target: shutil.copy2(f,data_target/f.name)
    db,imports=import_files(name,data_target)
    CACHE.pop(name,None); loaded=load_dashboard(name)
    return {'dashboard':name,'project_folder':str(project.relative_to(target)),'pbip':pbips[0].name,'metadata':loaded['summary'],'dataset_imports':imports,'database':str(db)}
@app.post('/api/reindex/{name}')
def reindex(name):
    safe_dashboard(name); CACHE.pop(name,None); item=load_dashboard(name)
    data=ROOT/'data'/name; imported=[]
    if data.exists(): _,imported=import_files(name,data)
    CACHE.pop(name,None); item=load_dashboard(name)
    return {'ok':True,'dashboard':name,'documents':len(item['docs']),'measures':len(item['summary']['measures']),'tables':len(item['summary']['tables']),'imports':imported}
@app.get('/api/dashboards/{name}/model')
def model(name): return load_dashboard(name)['summary']
def _format_net_sales_answer(question, result, sql_reason):
    """Render SQL-backed Net Sales values directly; do not let an LLM rewrite numbers."""
    rows = result.get('rows', []) if result else []
    if not rows:
        return 'The Net Sales query ran successfully, but it returned no rows for the selected filters.'
    is_category = any('category' in str(k).lower() for k in rows[0])
    if is_category:
        lines = ['**Net Sales by category**', '', '| Category | Net Sales |', '|---|---:|']
        total = 0.0
        for row in rows:
            category = str(row.get('Category', 'Unspecified'))
            value = row.get('NetSales')
            try:
                number = float(value or 0)
                total += number
                formatted = f'{number:,.2f}'
            except (TypeError, ValueError):
                formatted = str(value)
            lines.append(f'| {category.replace("|", "\\|")} | {formatted} |')
        lines += ['', f'**Total across returned categories:** {total:,.2f}', '',
                  '**Calculation used:** Quantity × Unit Price × (1 − Line Discount) × (1 − Order Discount Rate).',
                  'Only orders with status **Completed** or **Shipped** are included.',
                  '', '_This follows the supplied Power BI [Net Sales] measure: [Sales After Line Discount] − [Order Discount Amount]._']
        if sql_reason:
            lines += ['', f'_{sql_reason}_']
        return '\n'.join(lines)
    value = rows[0].get('NetSales')
    try: formatted = f'{float(value):,.2f}'
    except (TypeError, ValueError): formatted = str(value)
    return ('**Net Sales:** ' + formatted + '\n\n'
            '**Calculation:** Quantity × Unit Price × (1 − Line Discount) × (1 − Order Discount Rate). '
            'Only Completed and Shipped orders are included.\n\n'
            '_This follows the supplied Power BI [Net Sales] measure: [Sales After Line Discount] − [Order Discount Amount]._')


def _process_chat(chat_id, question, selected):
    item=load_dashboard(selected)
    if item.get('rag') is None:
        item['rag']=DashboardRAG(item['docs'])
    # Parallelize independent I/O/retrieval work. SQLite remains read-only and serialized per query.
    with ThreadPoolExecutor(max_workers=3) as pool:
        docs_future = pool.submit(item['rag'].retrieve, question, 6)
        history_future = pool.submit(history_text, chat_id)
        schema_future = pool.submit(schema_for, db_path(selected))
        docs = docs_future.result()
        hist = history_future.result()
        schema = schema_future.result()
    context='\n\n'.join(f"SOURCE: {d['source']}\n{d['text']}" for d in docs)
    sql=''; sql_reason=''; sql_result=''
    if db_path(selected).exists() and re.search(r'\b(sales|revenue|profit|orders?|customers?|quantity|units|count|total|average|avg|maximum|minimum|highest|lowest|top|bottom|by channel|by region|by product|compare|trend|sum|how many|多少)\b', question, re.I):
        try:
            proposed,sql_reason=propose_sql(question,schema,context,hist)
            if proposed:
                result=execute_readonly(proposed,db_path(selected))
                sql=proposed
                sql_result=json.dumps(result,ensure_ascii=False,default=str)
        except Exception as e:
            sql_reason=f'SQL not executed: {type(e).__name__}: {e}'
    try:
        if sql and re.search(r'\bnet\s*sales\b', question, re.I) and sql_result:
            response = _format_net_sales_answer(question, json.loads(sql_result), sql_reason)
        else:
            response=llm_answer(question,context,sql_result,hist,selected,sql_reason,schema)
    except Exception as e:
        response=f'BI-GPT could not complete the response: {type(e).__name__}: {e}. Check the app and database logs. Retrieved context: '+(context[:1800] or 'No matching Power BI metadata.')
    if sql: response+='\n\n**SQL used (read-only):**\n```sql\n'+sql+'\n```'
    elif sql_reason: response+='\n\n_Data query note: '+sql_reason+'_'
    if docs: response+='\n\n_Sources: '+', '.join(d['source'] for d in docs[:5])+'_'
    store.add_message(chat_id,'assistant',response)
    return {'answer':response,'chat_id':chat_id,'dashboard':selected,'sources':[{'name':d['source'],'score':round(d['score'],3)} for d in docs],'sql':sql,'sql_reason':sql_reason}

def _run_chat_job(job_id, chat_id, question, selected):
    try:
        result=_process_chat(chat_id,question,selected)
        with CHAT_JOBS_LOCK:
            CHAT_JOBS[job_id]={'status':'completed','result':result}
    except Exception as e:
        with CHAT_JOBS_LOCK:
            CHAT_JOBS[job_id]={'status':'failed','error':f'{type(e).__name__}: {e}'}

@app.post('/api/chat/start')
def start_chat(body:ChatRequest):
    q=body.question.strip()
    if not q: raise HTTPException(400,'Question cannot be empty.')
    chatdata=store.get_chat(body.chat_id)
    if not chatdata: raise HTTPException(404,'Chat not found. Create a new chat first.')
    selected=body.dashboard or chatdata['chat'].get('dashboard')
    if not selected: raise HTTPException(400,'Select a dashboard before asking a question.')
    safe_dashboard(selected)
    store.add_message(body.chat_id,'user',q)
    job_id=str(uuid.uuid4())
    with CHAT_JOBS_LOCK:
        CHAT_JOBS[job_id]={'status':'running'}
    CHAT_EXECUTOR.submit(_run_chat_job,job_id,body.chat_id,q,selected)
    return {'job_id':job_id,'status':'running','chat_id':body.chat_id}

@app.get('/api/chat/status/{job_id}')
def chat_status(job_id):
    with CHAT_JOBS_LOCK:
        job=CHAT_JOBS.get(job_id)
    if not job: raise HTTPException(404,'Chat job not found or expired.')
    return job

@app.post('/api/chat')
def chat(body:ChatRequest):
    q=body.question.strip()
    if not q: raise HTTPException(400,'Question cannot be empty.')
    chatdata=store.get_chat(body.chat_id)
    if not chatdata: raise HTTPException(404,'Chat not found. Create a new chat first.')
    selected=body.dashboard or chatdata['chat'].get('dashboard')
    if not selected: raise HTTPException(400,'Select a dashboard before asking a question.')
    safe_dashboard(selected)
    store.add_message(body.chat_id,'user',q)
    return _process_chat(body.chat_id,q,selected)
@app.get('/api/health')
def health():
    return {'status':'ok','version':'3.8.0','ollama_model':__import__('os').getenv('OLLAMA_MODEL','llama3.2:3b'),'dashboards':dashboard_names()}

@app.get('/api/diagnostics')
def diagnostics():
    return {
        'status':'ok',
        'version':'3.8.0',
        'project_root':str(ROOT),
        'dashboard_names':dashboard_names(),
        'ollama_url':__import__('os').getenv('OLLAMA_BASE_URL','http://127.0.0.1:11434'),'rag_mode':__import__('os').getenv('RAG_MODE','tfidf'),'request_timeout':__import__('os').getenv('OLLAMA_REQUEST_TIMEOUT','300'),'data_workers':__import__('os').getenv('BI_GPT_DATA_WORKERS','4')
    }
