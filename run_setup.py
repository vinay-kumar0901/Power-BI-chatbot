from pathlib import Path
from app import store
from app.config import ROOT
from app.datasets import import_files
from app.main import dashboard_names, load_dashboard, CACHE

store.init_store()
for name in dashboard_names():
    try:
        # Import CSV/XLSX exports before constructing the metadata/RAG documents,
        # so the current SQL schema is included on the first chat request.
        data = ROOT / 'data' / name
        imported = []
        if data.exists():
            _, imported = import_files(name, data)
        CACHE.pop(name, None)
        info = load_dashboard(name)
        print(
            f"Dashboard: {name} | Tables in model: {len(info['summary']['tables'])} "
            f"| DAX measures: {len(info['summary']['measures'])} "
            f"| Pages: {len(info['summary']['pages'])}"
        )
        if imported:
            print('Imported datasets:', imported)
    except Exception as e:
        print(f'Warning: {name}: {type(e).__name__}: {e}')
print('Setup complete. Start: uvicorn app.main:app --host 0.0.0.0 --port 8000')
