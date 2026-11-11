"""Publish documented content revisions without replacing unrelated owner edits."""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def mapping(row,fields):
    return dict(row) if hasattr(row,'keys') else dict(zip(fields,row))


def revise(data,edits):
    result=dict(data)
    for edit in edits:
        field=edit['field']
        if field not in ('title','subtitle','body','sources'):
            raise ValueError('Unsupported editorial field')
        value=result.get(field,'')
        if edit['old'] not in value:
            return None
        result[field]=value.replace(edit['old'],edit['new'],1)
    return result


def apply(connection,sql):
    package=json.loads((Path(__file__).resolve().parents[1]/'editorial/reporting/2026-11-10-content-review.json').read_text())
    for change in package:
        cursor=connection.execute(sql('SELECT * FROM articles WHERE id=?'),(change['article_id'],))
        row=cursor.fetchone()
        if row is None:
            continue
        article=mapping(row,tuple(c[0] for c in cursor.description))
        if article['status']!='published' or article['locale']!='fr':
            continue
        updated=revise(article,change['locales']['fr'])
        if updated is None:
            continue
        translations={}
        for row in connection.execute(sql("SELECT locale,data,manual FROM translations WHERE target_type='article' AND target_id=? AND version=?"),(article['id'],article['updated_at'])).fetchall():
            tr=mapping(row,('locale','data','manual'))
            if tr['locale'] not in ('en','pt-BR','es'):
                continue
            data=revise(json.loads(tr['data']),change['locales'][tr['locale']])
            if data is None:
                break
            if 'sources' in data:
                for edit in change['locales']['fr']:
                    if edit['field']=='sources':
                        data['sources']=data['sources'].replace(edit['old'],edit['new'],1)
            translations[tr['locale']]=(data,tr['manual'])
        if set(translations)!= {'en','pt-BR','es'}:
            continue
        stamp=datetime.now(timezone.utc).isoformat()
        count=connection.execute(sql('UPDATE articles SET title=?,subtitle=?,body=?,sources=?,updated_at=? WHERE id=? AND updated_at=? AND body=?'),
            (updated['title'],updated['subtitle'],updated['body'],updated['sources'],stamp,article['id'],article['updated_at'],article['body'])).rowcount
        if not count:
            continue
        revision=dict(article)
        if change.get('notes'):
            revision['correction_note']=change['notes']['fr']
            revision['correction_notes']=change['notes']
        connection.execute(sql('INSERT INTO revisions VALUES (?,?,?,?,?)'),
            (str(uuid.uuid4()),article['id'],json.dumps(revision,ensure_ascii=False),'system:editorial-review',stamp))
        for locale,(data,manual) in translations.items():
            connection.execute(sql("INSERT INTO translations VALUES (?,'article',?,?,?,?,?,?) ON CONFLICT(target_type,target_id,version,locale) DO NOTHING"),
                (str(uuid.uuid4()),article['id'],stamp,locale,json.dumps(data,ensure_ascii=False),manual,stamp))
