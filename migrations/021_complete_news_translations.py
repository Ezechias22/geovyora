"""Add version-matched editorial translations without replacing existing edits."""
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def apply(connection, sql):
    root = Path(__file__).resolve().parents[1] / 'editorial' / 'translations'
    hashes = json.loads((root / 'source_hashes.json').read_text(encoding='utf-8'))
    stamp = datetime.now(timezone.utc).isoformat()
    fields = ('id', 'title', 'subtitle', 'body', 'updated_at')
    for locale in ('en', 'pt-BR', 'es'):
        translations = json.loads((root / (locale+'.json')).read_text(encoding='utf-8'))
        for article_id, data in translations.items():
            row = connection.execute(sql('SELECT id,title,subtitle,body,updated_at FROM articles WHERE id=?'), (article_id,)).fetchone()
            if row is None:
                continue
            article = dict(row) if hasattr(row, 'keys') else dict(zip(fields, row))
            digest = hashlib.sha256('\0'.join(article[key] for key in ('title', 'subtitle', 'body')).encode()).hexdigest()
            # Do not attach an older translation to an article edited in production.
            if digest != hashes[article_id]:
                continue
            connection.execute(sql(
                'INSERT INTO translations(id,target_type,target_id,version,locale,data,manual,created_at) '
                "VALUES (?,'article',?,?,?,?,1,?) ON CONFLICT(target_type,target_id,version,locale) DO NOTHING"
            ), (str(uuid.uuid4()), article_id, article['updated_at'], locale,
                json.dumps(data, ensure_ascii=False), stamp))
