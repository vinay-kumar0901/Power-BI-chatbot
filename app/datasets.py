from pathlib import Path
import sqlite3, pandas as pd, re, os
from concurrent.futures import ProcessPoolExecutor, as_completed
from .config import STORAGE

def safe_name(s):
    s=re.sub(r'[^A-Za-z0-9_]+','_',Path(s).stem).strip('_')
    return (s or 'dataset')[:55]
def db_path(dashboard): return STORAGE / f"{safe_name(dashboard)}.sqlite3"
def _read_sheet_task(file_path, sheet_name, table_source):
    """Process-pool worker: load one independent CSV/Excel sheet."""
    f = Path(file_path)
    if f.suffix.lower() == '.csv':
        df = pd.read_csv(f, low_memory=False)
    else:
        df = pd.read_excel(f, sheet_name=sheet_name)
    return f.name, table_source, df

def import_files(dashboard, files_dir: Path):
    files = sorted(list(files_dir.rglob('*.csv')) + list(files_dir.rglob('*.xlsx')) + list(files_dir.rglob('*.xls')))
    db = db_path(dashboard)
    imported = []
    if not files:
        return db, imported

    # Build independent file/sheet tasks. This also parallelizes a single multi-sheet
    # workbook, which is the common bundled-dashboard case in Colab.
    tasks = []
    for f in files:
        if f.suffix.lower() == '.csv':
            tasks.append((str(f), f.stem, f.stem))
        else:
            try:
                sheet_names = pd.ExcelFile(f).sheet_names
                for sheet in sheet_names:
                    table_source = sheet if len(sheet_names) > 1 else f.stem
                    tasks.append((str(f), sheet, table_source))
            except Exception as exc:
                imported.append({'file': f.name, 'error': f'{type(exc).__name__}: {exc}'})

    workers = max(1, min(len(tasks), int(os.getenv('BI_GPT_DATA_WORKERS', min(os.cpu_count() or 1, 4)))))
    loaded = []
    if workers > 1 and tasks:
        try:
            with ProcessPoolExecutor(max_workers=workers) as pool:
                futures = [pool.submit(_read_sheet_task, *task) for task in tasks]
                for future in as_completed(futures):
                    loaded.append(future.result())
        except Exception:
            # Process spawning can be restricted in some notebook/Windows contexts.
            loaded = []
    if not loaded and tasks:
        for task in tasks:
            try:
                loaded.append(_read_sheet_task(*task))
            except Exception as exc:
                imported.append({'file': Path(task[0]).name, 'table': task[2], 'error': f'{type(exc).__name__}: {exc}'})

    # One SQLite writer avoids concurrent-write locks; expensive workbook reads run in parallel.
    with sqlite3.connect(db) as conn:
        for filename, table_source, df in loaded:
            try:
                if df.empty:
                    continue
                df.columns = [str(c).strip() for c in df.columns]
                if table_source.lower().startswith('data_'):
                    table_source = table_source[5:]
                table = safe_name(table_source)
                df.to_sql(table, conn, if_exists='replace', index=False)
                imported.append({'file': filename, 'table': table, 'rows': len(df), 'columns': list(df.columns)})
            except Exception as exc:
                imported.append({'file': filename, 'table': str(table_source), 'error': f'{type(exc).__name__}: {exc}'})
    return db, imported

def schema_for(db):
    if not db.exists(): return 'No uploaded CSV/XLSX datasets have been imported.'
    lines=[]
    with sqlite3.connect(db) as c:
        tables=[r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        for t in tables:
            cols=[r[1]+' '+r[2] for r in c.execute(f'PRAGMA table_info("{t}")')]
            lines.append(f'TABLE {t}: '+', '.join(cols))
    return '\n'.join(lines) or 'Database contains no tables.'
