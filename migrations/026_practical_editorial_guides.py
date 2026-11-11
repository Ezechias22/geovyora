"""Publish two original practical guides and their translations atomically."""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def apply(connection, sql):
    articles = json.loads((Path(__file__).resolve().parents[1] / 'editorial/news/2026-11-10-practical-guides.json').read_text(encoding='utf-8'))
    stamp = datetime.now(timezone.utc).isoformat()
    connection.execute(sql("INSERT INTO categories(id,name,slug,sort_order,active) VALUES ('geovyora-societe','Société','societe',20,1) ON CONFLICT DO NOTHING"))
    for article in articles:
        inserted = connection.execute(sql(
            "INSERT INTO articles(id,slug,title,subtitle,body,category,region,author,locale,status,"
            "demo,sponsored,featured,publish_at,created_at,updated_at,sources,tags,kind) "
            "VALUES (?,?,?,?,?,?,?,'Geovyora','fr','published',0,0,0,?,?,?,?,?,'guide') ON CONFLICT DO NOTHING"
        ), (article['id'], article['slug'], article['title'], article['subtitle'], article['body'],
            article['category'], article['region'], stamp, stamp, stamp, '\n'.join(article['sources']), article['tags'])).rowcount
        # Existing content, including deletions and editorial changes, is never replaced.
        if not inserted:
            continue
        for locale, data in article['translations'].items():
            connection.execute(sql(
                "INSERT INTO translations VALUES (?,'article',?,?,?,?,1,?) "
                "ON CONFLICT(target_type,target_id,version,locale) DO NOTHING"
            ), (str(uuid.uuid4()), article['id'], stamp, locale, json.dumps(data, ensure_ascii=False), stamp))
