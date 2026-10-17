import os, sqlite3, threading, importlib.util
from pathlib import Path
from contextlib import contextmanager
ROOT=Path(__file__).parent
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT/'.env')
except ImportError: pass
LOCK=threading.RLock()
URL=os.getenv('DATABASE_URL','')
PATH=os.getenv('SQLITE_PATH',str(ROOT/'data'/'vyora.sqlite3'))
@contextmanager
def connection():
    with LOCK:
        if URL:
            import psycopg
            from psycopg.rows import dict_row
            c=psycopg.connect(URL,row_factory=dict_row)
        else:
            Path(PATH).parent.mkdir(parents=True,exist_ok=True)
            c=sqlite3.connect(PATH,timeout=30); c.row_factory=sqlite3.Row
            c.execute('PRAGMA foreign_keys=ON'); c.execute('PRAGMA journal_mode=WAL')
        try:
            yield c
            c.commit()
        except Exception:
            c.rollback(); raise
        finally: c.close()
def sql(query): return query.replace('?', '%s') if URL else query
def rows(query,args=()):
    with connection() as c: return [dict(r) for r in c.execute(sql(query),args).fetchall()]
def one(query,args=()):
    r=rows(query,args); return r[0] if r else None
def write(query,args=()):
    with connection() as c: return c.execute(sql(query),args).rowcount
def migrate():
    with connection() as c:
        if URL:c.execute('SELECT pg_advisory_xact_lock(861410073)')
        else:c.execute('BEGIN IMMEDIATE')
        c.execute('CREATE TABLE IF NOT EXISTS schema_migrations(version TEXT PRIMARY KEY)')
        migrations=sorted([*ROOT.joinpath('migrations').glob('*.sql'),*ROOT.joinpath('migrations').glob('*.py')],key=lambda p:p.name)
        for p in migrations:
            if not c.execute(sql('SELECT version FROM schema_migrations WHERE version=?'),(p.name,)).fetchone():
                if p.suffix=='.sql':
                    for statement in p.read_text(encoding='utf-8-sig').split(';'):
                        if statement.strip(): c.execute(statement)
                else:
                    spec=importlib.util.spec_from_file_location('geovyora_migration_'+p.stem.replace('-','_'),p)
                    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                    module.apply(c,sql)
                c.execute(sql('INSERT INTO schema_migrations(version) VALUES (?)'),(p.name,))
