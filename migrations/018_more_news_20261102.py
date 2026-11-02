"""Publish additional verified coverage without changing earlier articles."""
import json
from datetime import datetime, timezone
from pathlib import Path


def apply(connection, sql):
    articles = json.loads((Path(__file__).resolve().parents[1] / 'editorial' / 'news' / '2026-11-02-suite.json').read_text(encoding='utf-8'))
    stamp = datetime.now(timezone.utc).isoformat()
    connection.execute(sql(
        "INSERT INTO categories(id,name,slug,sort_order,active) VALUES (?,?,?,20,1) ON CONFLICT DO NOTHING"
    ), ('geovyora-societe', 'Société', 'societe'))
    for article in articles:
        connection.execute(sql(
            "INSERT INTO articles(id,slug,title,subtitle,body,category,region,author,locale,status,"
            "demo,sponsored,featured,publish_at,created_at,updated_at,sources,tags) "
            "VALUES (?,?,?,?,?,'Société',?,'Geovyora','fr','published',0,0,0,?,?,?,?,?) "
            "ON CONFLICT DO NOTHING"
        ), (article['id'], article['slug'], article['title'], article['subtitle'], article['body'],
            article['region'], stamp, stamp, stamp, '\n'.join(article['sources']), article['tags']))
