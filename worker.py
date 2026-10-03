"""Run as a separate process: publication, translations, campaigns, housekeeping."""
import time,logging
from datetime import datetime,timezone
from db import migrate,write,rows
from jobs import process_translation_jobs,process_push_jobs,queue_translation,PRIMARY

def tick():
    stamp=datetime.now(timezone.utc).isoformat()
    published=write("UPDATE articles SET status='published',updated_at=? WHERE status='scheduled' AND publish_at<=?",(stamp,stamp))
    write('DELETE FROM sessions WHERE expires<?',(int(time.time()),))
    write('DELETE FROM rate_limits WHERE reset_at<?',(int(time.time()),))
    write('DELETE FROM visitor_bans WHERE expires_at<?',(stamp,))
    # Prepares the primary languages; comments only translate on explicit reader request.
    for article in rows("SELECT * FROM articles WHERE status='published' ORDER BY updated_at DESC LIMIT 100"):
        for lang in PRIMARY:
            if lang!=article['locale']:queue_translation('article',article,lang)
    process_translation_jobs();process_push_jobs()
    return published
if __name__=='__main__':
    migrate()
    from extensions import initialize_features
    initialize_features()
    while True:
        try:tick()
        except Exception:logging.exception('Worker failed; retry in 15 seconds.')
        time.sleep(15)
