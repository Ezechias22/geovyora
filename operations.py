"""Offline deployment checks and consistent database backup/restore."""
import argparse, json, os, sqlite3, subprocess
from pathlib import Path
from urllib.parse import urlparse
import db

def checks():
    site=urlparse(os.getenv('SITE_URL',''))
    return {
        'https_domain': site.scheme=='https' and bool(site.hostname) and site.hostname not in {'localhost','127.0.0.1'},
        'secure_cookies': os.getenv('COOKIE_SECURE')=='1',
        'postgresql': bool(db.URL),
        'mux': all(os.getenv(k) for k in ['MUX_TOKEN_ID','MUX_TOKEN_SECRET','MUX_WEBHOOK_SECRET']),
        'translation': bool(os.getenv('GOOGLE_TRANSLATION_KEY')),
        'firebase': all(os.getenv(k) for k in ['FIREBASE_PUBLIC_CONFIG','FIREBASE_VAPID_KEY','FIREBASE_SERVICE_ACCOUNT']),
        'images': all(os.getenv(k) for k in ['S3_BUCKET','S3_ACCESS_KEY_ID','S3_SECRET_ACCESS_KEY','MEDIA_PUBLIC_URL']),
        'private_submission_bucket': bool(os.getenv('PRIVATE_SUBMISSION_BUCKET')),
    }

def backup(target):
    target=Path(target).resolve()
    if target.exists(): raise ValueError('Destination already exists; choose a new filename.')
    target.parent.mkdir(parents=True,exist_ok=True)
    # Restrict sensitive backup permissions before writing any bytes.
    fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.close(fd)
    try:
        if db.URL:
            env=os.environ.copy();env['PGDATABASE']=db.URL
            subprocess.run(['pg_dump','--format=custom','--file',str(target)],env=env,check=True)
        else:
            source=Path(db.PATH).resolve()
            if not source.exists():raise ValueError('Source database does not exist.')
            with sqlite3.connect(source) as src, sqlite3.connect(target) as dst:
                src.backup(dst)
                if dst.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Backup integrity check failed.')
    except Exception:
        target.unlink(missing_ok=True);raise
    return target

def restore_sqlite(source,target):
    source=Path(source).resolve();target=Path(target).resolve()
    if not source.is_file():raise ValueError('Backup not found.')
    if target.exists():raise ValueError('Restore only to a new database path; existing databases are never overwritten.')
    target.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(f'{source.as_uri()}?mode=ro',uri=True) as src:
        if src.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Invalid backup.')
        fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.close(fd)
        try:
            with sqlite3.connect(target) as dst:src.backup(dst)
        except Exception:target.unlink(missing_ok=True);raise
    return target

if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('check')
    b=sub.add_parser('backup');b.add_argument('output')
    r=sub.add_parser('restore-sqlite');r.add_argument('backup');r.add_argument('new_database')
    a=p.parse_args()
    try:
        if a.command=='check':
            result=checks();print(json.dumps(result,indent=2));raise SystemExit(0 if all(result.values()) else 1)
        print(backup(a.output) if a.command=='backup' else restore_sqlite(a.backup,a.new_database))
    except (ValueError,subprocess.CalledProcessError,FileNotFoundError) as e:
        # Do not print connection URLs or service secrets.
        raise SystemExit('Operation failed: '+(str(e) if isinstance(e,ValueError) else 'database utility missing or command failed.'))
