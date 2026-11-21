from pathlib import Path
import os
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
STORAGE = ROOT / 'storage'
UPLOADS = ROOT / 'uploads'
DASHBOARDS = ROOT / 'powerbi'
DATA = ROOT / 'data'
for p in (STORAGE, UPLOADS, DASHBOARDS, DATA): p.mkdir(parents=True, exist_ok=True)
OLLAMA_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434').rstrip('/')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:1b')
OLLAMA_REQUEST_TIMEOUT = int(os.getenv('OLLAMA_REQUEST_TIMEOUT', '300'))
OLLAMA_CONNECT_TIMEOUT = int(os.getenv('OLLAMA_CONNECT_TIMEOUT', '10'))
OLLAMA_NUM_THREADS = int(os.getenv('OLLAMA_NUM_THREADS', str(min(os.cpu_count() or 2, 8))))
RAG_MODE = os.getenv('RAG_MODE', 'tfidf').lower()
