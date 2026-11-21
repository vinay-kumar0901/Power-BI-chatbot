import sqlite3, uuid
from datetime import datetime, timezone
from .config import STORAGE
DB = STORAGE / 'conversations.sqlite3'
def connect():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init_store():
    with connect() as c:
        c.executescript('''CREATE TABLE IF NOT EXISTS chats(id TEXT PRIMARY KEY,title TEXT NOT NULL,dashboard TEXT,created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT,chat_id TEXT NOT NULL,role TEXT NOT NULL,content TEXT NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(chat_id) REFERENCES chats(id));''')
def now(): return datetime.now(timezone.utc).isoformat()
def create_chat(dashboard=None):
    cid=str(uuid.uuid4()); t=now()
    with connect() as c: c.execute('INSERT INTO chats VALUES(?,?,?,?,?)',(cid,'New chat',dashboard,t,t))
    return cid
def list_chats():
    with connect() as c: return [dict(x) for x in c.execute('SELECT id,title,dashboard,created_at,updated_at FROM chats ORDER BY updated_at DESC')]
def get_chat(cid):
    with connect() as c:
        chat=c.execute('SELECT * FROM chats WHERE id=?',(cid,)).fetchone()
        if not chat: return None
        msgs=[dict(x) for x in c.execute('SELECT role,content,created_at FROM messages WHERE chat_id=? ORDER BY id',(cid,))]
        return {'chat':dict(chat),'messages':msgs}
def add_message(cid,role,content):
    t=now()
    with connect() as c:
        c.execute('INSERT INTO messages(chat_id,role,content,created_at) VALUES(?,?,?,?)',(cid,role,content,t))
        c.execute('UPDATE chats SET updated_at=? WHERE id=?',(t,cid))
        if role=='user':
            row=c.execute('SELECT title FROM chats WHERE id=?',(cid,)).fetchone()
            if row and row['title']=='New chat': c.execute('UPDATE chats SET title=? WHERE id=?',(content[:55],cid))
def delete_chat(cid):
    with connect() as c: c.execute('DELETE FROM messages WHERE chat_id=?',(cid,)); c.execute('DELETE FROM chats WHERE id=?',(cid,))
