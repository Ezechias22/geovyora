"""Remove preparation boilerplate without inventing human reporting credits."""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def apply(connection, sql):
    changes=json.loads((Path(__file__).resolve().parents[1]/'editorial/audit/2026-11-10-reader-copy-changes.json').read_text())
    for change in changes:
        cursor=connection.execute(sql('SELECT * FROM articles WHERE id=?'),(change['article_id'],))
        row=cursor.fetchone()
        if row is None:
            continue
        article=dict(row) if hasattr(row,'keys') else dict(zip((col[0] for col in cursor.description),row))
        field=change.get('field','body')
        if field not in ('body','image_credit'):
            raise ValueError('Unsupported copy field')
        edit=change['locales']['fr']
        if edit['old'] not in article[field]:
            continue
        stamp=datetime.now(timezone.utc).isoformat()
        updated=connection.execute(sql('UPDATE articles SET '+field+'=?,updated_at=? WHERE id=? AND updated_at=? AND '+field+'=?'),
            (article[field].replace(edit['old'],edit['new'],1),stamp,article['id'],article['updated_at'],article[field])).rowcount
        if not updated:
            continue
        connection.execute(sql('INSERT INTO revisions VALUES (?,?,?,?,?)'),
            (str(uuid.uuid4()),article['id'],json.dumps(article,ensure_ascii=False),'system:reader-copy',stamp))
        for row in connection.execute(sql("SELECT locale,data,manual FROM translations WHERE target_type='article' AND target_id=? AND version=?"),(article['id'],article['updated_at'])).fetchall():
            tr=dict(row) if hasattr(row,'keys') else dict(zip(('locale','data','manual'),row))
            data=json.loads(tr['data']);edit=change['locales'].get(tr['locale'])
            if edit and edit['old'] in data.get(field,''):
                data[field]=data[field].replace(edit['old'],edit['new'],1)
            connection.execute(sql("INSERT INTO translations VALUES (?,'article',?,?,?,?,?,?) ON CONFLICT(target_type,target_id,version,locale) DO NOTHING"),
                (str(uuid.uuid4()),article['id'],stamp,tr['locale'],json.dumps(data,ensure_ascii=False),tr['manual'],stamp))
