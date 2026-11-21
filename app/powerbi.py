"""Extract useful metadata from a Power BI Project (PBIP) folder."""
from pathlib import Path
import json, re

def read_text(path):
    try: return path.read_text(encoding='utf-8-sig', errors='ignore')
    except Exception: return ''

def extract_dashboard(project_dir: Path):
    docs=[]; summary={'project':project_dir.name,'pbip_files':[],'tables':[],'measures':[],'relationships':[],'pages':[],'visuals':[],'sources':[]}
    if not project_dir.exists(): return summary, docs
    for pbip in project_dir.rglob('*.pbip'):
        summary['pbip_files'].append(str(pbip.relative_to(project_dir)))
        docs.append({'source':pbip.name,'text':read_text(pbip)[:12000]})
    # TMDL model files: parse table and measure declarations and preserve full source for RAG.
    for f in project_dir.rglob('*.tmdl'):
        if any(x in f.parts for x in ['.git','.pbi']): continue
        txt=read_text(f)
        table_names=re.findall(r'(?m)^\s*table\s+(.+?)\s*$',txt)
        for t in table_names:
            if t.strip("'\"") not in summary['tables']: summary['tables'].append(t.strip("'\""))
        # TMDL measures can be indented: measure Name = expression
        for m in re.finditer(r"(?m)^\s*measure\s+(.+?)\s*=\s*(.*(?:\n(?!\s*(?:measure|column|partition|table|relationship)\b).*)*)",txt):
            item={'name':m.group(1).strip().strip("'\""),'expression':m.group(2).strip()[:3000],'file':str(f.relative_to(project_dir))}
            summary['measures'].append(item)
        docs.append({'source':str(f.relative_to(project_dir)),'text':txt[:18000]})
    # Legacy model.bim JSON
    for f in project_dir.rglob('model.bim'):
        try:
            model=json.loads(read_text(f)); model_tables=model.get('model',{}).get('tables',[])
            for t in model_tables:
                name=t.get('name','')
                if name and name not in summary['tables']: summary['tables'].append(name)
                for m in t.get('measures',[]): summary['measures'].append({'name':m.get('name'),'expression':m.get('expression',''),'table':name,'file':str(f.relative_to(project_dir))})
            summary['relationships']=model.get('model',{}).get('relationships',[])
        except Exception: pass
    for f in project_dir.rglob('page.json'):
        try:
            obj=json.loads(read_text(f)); page=obj.get('name',f.parent.name)
            summary['pages'].append(page); docs.append({'source':str(f.relative_to(project_dir)),'text':json.dumps(obj,ensure_ascii=False)[:12000]})
        except Exception: pass
    for f in project_dir.rglob('visual.json'):
        try:
            obj=json.loads(read_text(f)); summary['visuals'].append(str(f.relative_to(project_dir)))
            docs.append({'source':str(f.relative_to(project_dir)),'text':json.dumps(obj,ensure_ascii=False)[:10000]})
        except Exception: pass
    # Report/semantic definition metadata and model relationships in TMDL.
    for f in project_dir.rglob('*.tmdl'):
        txt=read_text(f)
        for block in re.findall(r'(?ms)^\s*relationship\s+.*?(?=^\s*(?:relationship|table|measure|partition)\s+|\Z)',txt):
            summary['relationships'].append(block[:2000])
    # De-duplicate docs by source path.
    seen=set(); unique=[]
    for d in docs:
        if d['source'] not in seen and d['text'].strip(): seen.add(d['source']); unique.append(d)
    docs=unique
    summary['tables']=sorted(set(summary['tables']))
    return summary, docs
