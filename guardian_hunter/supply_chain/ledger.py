"""SQLite anti-replay reservation; local tampering resistance NOT claimed."""
import sqlite3
from .core import sha

def consume(db_path,authorization_id,context):
    if not isinstance(authorization_id,str) or not authorization_id or not isinstance(context,dict):raise ValueError('Invalid authorization context')
    context_hash=sha(context)
    with sqlite3.connect(db_path,timeout=10,isolation_level='IMMEDIATE') as db:
        db.execute('CREATE TABLE IF NOT EXISTS used (id TEXT PRIMARY KEY, context_hash TEXT NOT NULL)')
        try:db.execute('INSERT INTO used(id,context_hash) VALUES (?,?)',(authorization_id,context_hash))
        except sqlite3.IntegrityError:return False
    return True
