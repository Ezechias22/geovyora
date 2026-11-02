"""Admin-only, reversible removal with public visibility and callback checks."""
import hashlib
import hmac
import json
import time
import uuid
from unittest.mock import patch

import test_workflows as fixtures
from db import one, rows, write
from security import hash_password


class ContentTrash(fixtures.Fixture):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        write('INSERT INTO staff(id,email,name,password_hash,role) VALUES (?,?,?,?,?)',
              ('trash-admin', 'admin@test.local', 'Admin', hash_password('Test-Password-12345'), 'admin'))

    def create(self, kind):
        identifier = 'trash-test-'+uuid.uuid4().hex
        stamp = '2026-11-02T00:00:00+00:00'
        if kind == 'articles':
            write("INSERT INTO articles(id,slug,title,body,category,author,status,publish_at,created_at,updated_at) "
                  "VALUES (?,?,?,'Original article body.','Société','Author','published',?,?,?)",
                  (identifier, identifier, identifier, stamp, stamp, stamp))
        elif kind == 'influencers':
            write("INSERT INTO influencers(id,slug,name,username,origin,residence,category,bio,status,created_at) "
                  "VALUES (?,?,?,'test','Haiti','Brazil','Culture','An original biography.','published',?)",
                  (identifier, identifier, identifier, stamp))
        elif kind == 'videos':
            write("INSERT INTO videos(id,slug,title,asset_id,playback_id,status,created_at) VALUES (?,?,?,?,?,'ready',?)",
                  (identifier, identifier, identifier, 'asset-'+identifier, 'playback-'+identifier, stamp))
        else:
            write("INSERT INTO media_assets(id,object_key,url,content_type,status,staff_id,created_at) "
                  "VALUES (?,?,?,'image/jpeg','ready','trash-admin',?)",
                  (identifier, identifier, 'https://example.test/'+identifier+'.jpg', stamp))
        return identifier

    def action(self, client, token, kind, identifier, action='delete', **extra):
        return client.post('/admin/content/'+kind+'/'+identifier+'/'+action,
                           data={'csrf_token': token, 'confirm': 'yes', **extra}, follow_redirects=False)

    def test_four_content_types_can_be_removed_and_restored(self):
        client, token = self.login('admin')
        for kind, table in [('articles', 'articles'), ('influencers', 'influencers'),
                            ('videos', 'videos'), ('media', 'media_assets')]:
            with self.subTest(kind=kind):
                identifier = self.create(kind)
                confirmation = client.get('/admin/'+kind, params={'delete': identifier, 'lang': 'fr'})
                self.assertEqual(confirmation.status_code, 200)
                self.assertIn('Confirmer la suppression', confirmation.text)
                self.assertIn('name="confirm" value="yes" required', confirmation.text)
                if kind == 'articles':
                    for locale, label in [('fr', 'Confirmer la suppression'), ('en', 'Confirm deletion'),
                                          ('pt-BR', 'Confirmar exclusão'), ('es', 'Confirmar eliminación')]:
                        localized = client.get('/admin/articles', params={'delete': identifier, 'lang': locale})
                        self.assertEqual(localized.status_code, 200)
                        self.assertIn(label, localized.text)
                self.assertNotEqual(one('SELECT status FROM '+table+' WHERE id=?', (identifier,))['status'], 'deleted')
                self.assertEqual(self.action(client, token, kind, identifier).status_code, 303)
                self.assertEqual(one('SELECT status FROM '+table+' WHERE id=?', (identifier,))['status'], 'deleted')
                self.assertNotIn(identifier, client.get('/admin/'+kind).text)
                self.assertIn(identifier, client.get('/admin/trash').text)
                if kind in ('articles', 'influencers', 'videos'):
                    segment = {'articles': 'article', 'influencers': 'influencer', 'videos': 'video'}[kind]
                    self.assertEqual(self.c.get('/fr/'+segment+'/'+identifier).status_code, 404)
                self.assertNotIn(identifier, self.c.get('/sitemap.xml').text)
                self.assertEqual(self.action(client, token, kind, identifier, action='restore').status_code, 303)
                expected = 'draft' if kind in ('articles', 'influencers') else 'ready'
                self.assertEqual(one('SELECT status FROM '+table+' WHERE id=?', (identifier,))['status'], expected)
                self.assertFalse(one('SELECT * FROM content_trash WHERE content_id=?', (identifier,)))
                self.assertEqual(len(rows("SELECT * FROM audit_logs WHERE target_id=? AND action IN ('content.trash','content.restore')", (identifier,))), 2)

    def test_permissions_csrf_confirmation_and_origin_are_enforced(self):
        identifier = self.create('articles')
        admin, token = self.login()
        self.assertEqual(self.action(self.c, token, 'articles', identifier).status_code, 401)
        self.assertEqual(self.action(admin, 'invalid', 'articles', identifier).status_code, 403)
        self.assertEqual(self.action(admin, token, 'articles', identifier, confirm='').status_code, 422)
        response = admin.post('/admin/content/articles/'+identifier+'/delete',
                              data={'csrf_token': token, 'confirm': 'yes'}, headers={'origin': 'https://attacker.invalid'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.action(admin, token, 'staff', identifier).status_code, 404)
        for role in ('editor', 'moderator'):
            client, csrf = self.login(role)
            self.assertEqual(self.action(client, csrf, 'articles', identifier).status_code, 403)
            self.assertEqual(client.get('/admin/trash').status_code, 403)
            if role == 'editor':
                listing = client.get('/admin/articles').text
                self.assertNotIn('?delete=', listing)
                self.assertNotIn('href="/admin/trash"', listing)
        self.assertEqual(one('SELECT status FROM articles WHERE id=?', (identifier,))['status'], 'published')

    def test_deletion_keeps_translations_and_blocks_stale_editor_forms(self):
        identifier = self.create('articles')
        stamp = one('SELECT updated_at FROM articles WHERE id=?', (identifier,))['updated_at']
        write("INSERT INTO translations VALUES (?,'article',?,?,'en',?,1,?)",
              (uuid.uuid4().hex, identifier, stamp, json.dumps({'title': 'Translated title', 'body': 'Translated body.'}), stamp))
        client, token = self.login()
        self.assertEqual(self.action(client, token, 'articles', identifier).status_code, 303)
        self.assertEqual(self.action(client, token, 'articles', identifier).status_code, 303)
        self.assertEqual(len(rows("SELECT * FROM audit_logs WHERE target_id=? AND action='content.trash'", (identifier,))), 1)
        stale = client.post('/admin/articles/save', data={'id': identifier, 'csrf_token': token, 'status': 'published'})
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(client.get('/admin/articles?edit='+identifier).status_code, 404)
        self.assertEqual(self.action(client, token, 'articles', identifier, action='restore').status_code, 303)
        self.assertTrue(one("SELECT id FROM translations WHERE target_id=? AND version=? AND locale='en'", (identifier, stamp)))
        self.assertEqual(one('SELECT body FROM articles WHERE id=?', (identifier,))['body'], 'Original article body.')

    def test_late_mux_webhook_cannot_republish_a_deleted_video(self):
        identifier = self.create('videos')
        client, token = self.login()
        self.assertEqual(self.action(client, token, 'videos', identifier).status_code, 303)
        raw = json.dumps({'id': uuid.uuid4().hex, 'type': 'video.asset.ready',
                          'data': {'id': 'asset-'+identifier, 'passthrough': identifier,
                                   'playback_ids': [{'id': 'new-playback', 'policy': 'public'}]}}).encode()
        stamp = str(int(time.time()))
        signature = hmac.new(b'test-secret', stamp.encode()+b'.'+raw, hashlib.sha256).hexdigest()
        response = self.c.post('/api/webhooks/mux', content=raw, headers={'mux-signature': 't='+stamp+',v1='+signature})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(one('SELECT status FROM videos WHERE id=?', (identifier,))['status'], 'deleted')

    def test_deleted_photo_cannot_be_verified_back_into_the_library(self):
        identifier = self.create('media')
        client, token = self.login()
        self.assertEqual(self.action(client, token, 'media', identifier).status_code, 303)
        with patch('extensions.s3_client') as storage:
            response = client.post('/admin/media/verify', data={'id': identifier, 'csrf_token': token})
            self.assertEqual(response.status_code, 409)
            storage.assert_not_called()
        self.assertEqual(one('SELECT status FROM media_assets WHERE id=?', (identifier,))['status'], 'deleted')
