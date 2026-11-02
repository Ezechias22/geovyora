"""Reversible content removal. Provider files and related records are preserved."""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from db import URL, connection, one, rows, sql
from security import csrf, require, same_origin

router = APIRouter()
CONTENT_TYPES = {
    'articles': ('articles', 'title', 'Atik'),
    'videos': ('videos', 'title', 'Videyo / Mux'),
    'influencers': ('influencers', 'name', 'Pwofil medya'),
    'media': ('media_assets', 'url', 'Foto / Medya'),
}


def content_record(kind, item_id):
    if kind not in CONTENT_TYPES:
        raise HTTPException(404, 'Unknown content type')
    table, _, _ = CONTENT_TYPES[kind]
    return one('SELECT * FROM '+table+' WHERE id=?', (item_id,))


def ensure_not_trashed(kind, item_id):
    record = content_record(kind, item_id)
    if record and record['status'] == 'deleted':
        raise HTTPException(409, 'Restore this content from the trash before editing it.')


def trash_entries():
    entries = rows('SELECT * FROM content_trash ORDER BY deleted_at DESC')
    for entry in entries:
        record = content_record(entry['content_type'], entry['content_id'])
        _, title, label = CONTENT_TYPES[entry['content_type']]
        entry['title'] = record[title] if record else entry['content_id']
        entry['type_label'] = label
    return entries


async def change_content(request, kind, item_id, restoring=False):
    form = await request.form()
    user = csrf(request, form.get('csrf_token'))
    require(request, ['super_admin', 'admin'])
    same_origin(request)
    if form.get('confirm') != 'yes':
        raise HTTPException(422, 'Confirmation required')
    if kind not in CONTENT_TYPES:
        raise HTTPException(404, 'Unknown content type')
    table, _, _ = CONTENT_TYPES[kind]
    stamp = datetime.now(timezone.utc).isoformat()
    with connection() as database:
        if not URL:
            database.execute('BEGIN IMMEDIATE')
        query = 'SELECT status FROM '+table+' WHERE id=?'+(' FOR UPDATE' if URL else '')
        row = database.execute(sql(query), (item_id,)).fetchone()
        if row is None:
            raise HTTPException(404, 'Content not found')
        status = row['status']
        if restoring:
            entry = database.execute(sql('SELECT previous_status FROM content_trash WHERE content_type=? AND content_id=?'), (kind, item_id)).fetchone()
            if status != 'deleted' or entry is None:
                raise HTTPException(409, 'This content is not in the trash.')
            status = 'draft' if kind in ('articles', 'influencers') else entry['previous_status']
            database.execute(sql('UPDATE '+table+' SET status=? WHERE id=?'), (status, item_id))
            database.execute(sql('DELETE FROM content_trash WHERE content_type=? AND content_id=?'), (kind, item_id))
        else:
            if status == 'deleted':
                return RedirectResponse('/admin/'+kind+'?trashed=1', 303)
            database.execute(sql('INSERT INTO content_trash VALUES (?,?,?,?,?)'), (kind, item_id, status, user['id'], stamp))
            database.execute(sql("UPDATE "+table+" SET status='deleted' WHERE id=?"), (item_id,))
        database.execute(sql('INSERT INTO audit_logs VALUES (?,?,?,?,?,?)'),
                         (str(uuid.uuid4()), user['id'], 'content.restore' if restoring else 'content.trash', item_id, kind, stamp))
    return RedirectResponse('/admin/'+kind+('?restored=1' if restoring else '?trashed=1'), 303)


@router.post('/admin/content/{kind}/{item_id}/delete')
async def delete_content(request: Request, kind: str, item_id: str):
    return await change_content(request, kind, item_id)


@router.post('/admin/content/{kind}/{item_id}/restore')
async def restore_content(request: Request, kind: str, item_id: str):
    return await change_content(request, kind, item_id, restoring=True)
