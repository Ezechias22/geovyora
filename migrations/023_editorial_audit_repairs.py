"""Repair legacy layout and correct a future announcement stated as past fact."""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def mapping(row, fields):
    return dict(row) if hasattr(row, 'keys') else dict(zip(fields, row))


def apply(connection, sql):
    for article_id in ('geovyora-wilson-isidor-2026', 'geovyora-khaby-lame-ai-twin-2026'):
        row = connection.execute(sql('SELECT body FROM articles WHERE id=?'), (article_id,)).fetchone()
        if row:
            body = row['body'] if hasattr(row, 'keys') else row[0]
            if '\\n' in body:
                connection.execute(sql('UPDATE articles SET body=? WHERE id=? AND body=?'),
                                   (body.replace('\\n', '\n'), article_id, body))
        for row in connection.execute(sql("SELECT id,data FROM translations WHERE target_type='article' AND target_id=?"), (article_id,)).fetchall():
            translation = mapping(row, ('id', 'data'))
            data = json.loads(translation['data'])
            if '\\n' in data.get('body', ''):
                data['body'] = data['body'].replace('\\n', '\n')
                connection.execute(sql('UPDATE translations SET data=? WHERE id=?'),
                                   (json.dumps(data, ensure_ascii=False), translation['id']))

    changes = json.loads((Path(__file__).resolve().parents[1] / 'editorial/audit/2026-11-02-corrections.json').read_text(encoding='utf-8'))
    cursor = connection.execute(sql('SELECT * FROM articles WHERE id=?'), (changes['article_id'],))
    row = cursor.fetchone()
    if row is None:
        return
    article = mapping(row, tuple(column[0] for column in cursor.description))
    if changes['old']['fr'] not in article['body']:
        return
    stamp = datetime.now(timezone.utc).isoformat()
    revision = dict(article)
    revision['correction_note'] = changes['notes']['fr']
    revision['correction_notes'] = changes['notes']
    connection.execute(sql('INSERT INTO revisions VALUES (?,?,?,?,?)'),
                       (str(uuid.uuid4()), article['id'], json.dumps(revision, ensure_ascii=False), 'system:editorial-audit', stamp))
    connection.execute(sql('UPDATE articles SET body=?,updated_at=? WHERE id=?'),
                       (article['body'].replace(changes['old']['fr'], changes['new']['fr'], 1), stamp, article['id']))
    for row in connection.execute(sql("SELECT locale,data,manual FROM translations WHERE target_type='article' AND target_id=? AND version=?"),
                                  (article['id'], article['updated_at'])).fetchall():
        translation = mapping(row, ('locale', 'data', 'manual'))
        locale = translation['locale']
        if locale not in changes['old']:
            continue
        data = json.loads(translation['data'])
        if changes['old'][locale] not in data.get('body', ''):
            continue
        data['body'] = data['body'].replace(changes['old'][locale], changes['new'][locale], 1)
        connection.execute(sql("INSERT INTO translations VALUES (?,'article',?,?,?,?,?,?) ON CONFLICT(target_type,target_id,version,locale) DO NOTHING"),
                           (str(uuid.uuid4()), article['id'], stamp, locale, json.dumps(data, ensure_ascii=False), translation['manual'], stamp))
