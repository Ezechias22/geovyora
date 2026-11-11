"""Readability, source fidelity and publisher-transparency regression checks."""
import html
import importlib.util
import json
import re
import sqlite3
from pathlib import Path

import test_workflows as fixtures
from db import one

ROOT = Path(__file__).parent
CHANGES = json.loads((ROOT / 'editorial/audit/2026-11-02-corrections.json').read_text())


class EditorialAudit(fixtures.Fixture):
    def test_legacy_articles_render_paragraphs_and_headings_in_all_languages(self):
        for slug in ('wilson-isidor-deklarasyon-ayiti-repiblik-dominikenn', 'khaby-lame-jimo-dijital-ako-975-milyon'):
            for locale in ('fr', 'en', 'pt-BR', 'es'):
                with self.subTest(slug=slug, locale=locale):
                    response = self.c.get('/'+locale+'/article/'+slug)
                    self.assertEqual(response.status_code, 200)
                    body = response.text.split('id="translated-body"', 1)[1].split('class="article-foot"', 1)[0]
                    self.assertNotIn('\\n', body)
                    self.assertNotIn('## ', body)
                    self.assertGreaterEqual(body.count('<h2>'), 3)

    def test_wyclef_correction_and_history_are_translated(self):
        for locale in ('fr', 'en', 'pt-BR', 'es'):
            response = self.c.get('/'+locale+'/article/wyclef-jean-influence-haitienne-diaspora-fugees')
            self.assertEqual(response.status_code, 200)
            text = html.unescape(response.text)
            self.assertIn(CHANGES['new'][locale].split(' [Associated Press]')[0], text)
            self.assertIn(CHANGES['notes'][locale], text)
            self.assertNotIn(CHANGES['old'][locale].split(' [Associated Press]')[0], text)

    def test_publisher_relationship_and_author_schema_are_explicit(self):
        expected = {'fr': 'Geovyora est un projet de Haytiles', 'en': 'Geovyora is a project of Haytiles',
                    'pt-BR': 'a Geovyora é um projeto da Haytiles', 'es': 'Geovyora es un proyecto de Haytiles'}
        for locale, phrase in expected.items():
            response = self.c.get('/'+locale+'/article/haytiles-ezechias-toussaint-entrepreneuriat-numerique')
            self.assertEqual(response.status_code, 200)
            self.assertIn(phrase, html.unescape(response.text))
        response = self.c.get('/fr/article/haiti-insecurite-campagnes-proteger-civils')
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', response.text, re.S)[1])
        self.assertEqual(schema['author']['@type'], 'Organization')
        self.assertEqual(schema['author']['name'], 'Geovyora')
        policy = response.headers['content-security-policy']
        script = policy.split('script-src', 1)[1].split(';', 1)[0]
        connect = policy.split('connect-src', 1)[1].split(';', 1)[0]
        self.assertIn('https://ep2.adtrafficquality.google', script)
        self.assertIn('https://ep1.adtrafficquality.google', connect)
        self.assertNotIn('ep1.adtrafficquality.google', script)
        self.assertNotIn('ep2.adtrafficquality.google', connect)
        self.assertNotIn('*.adtrafficquality.google', policy)

    def test_google_verification_frames_are_limited_to_observed_paths(self):
        policy = self.c.get('/fr').headers['content-security-policy']
        directives = {part.strip().split()[0]: part.strip().split()[1:]
                      for part in policy.split(';') if part.strip()}
        frames = directives['frame-src']
        self.assertIn('https://ep2.adtrafficquality.google/sodar/', frames)
        self.assertIn('https://www.google.com/recaptcha/api2/aframe', frames)
        self.assertNotIn('https://ep2.adtrafficquality.google', frames)
        self.assertNotIn('https://www.google.com', frames)
        self.assertNotIn('*', frames)
        self.assertNotIn('https:', frames)
        self.assertNotIn("'unsafe-inline'", directives['script-src'])
        self.assertNotIn('https://www.google.com', directives['script-src'])
        self.assertNotIn('https://www.google.com', directives['connect-src'])
        self.assertEqual(directives['object-src'], ["'none'"])
        self.assertEqual(directives['form-action'], ["'self'"])

    def test_repair_migration_preserves_photos_and_translation_history(self):
        spec = importlib.util.spec_from_file_location('audit_repairs', ROOT / 'migrations/023_editorial_audit_repairs.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with sqlite3.connect(':memory:') as database:
            database.executescript((ROOT / 'migrations/001_initial.sql').read_text())
            records = [('geovyora-wilson-isidor-2026', 'Introduction\\n\\n## Heading\\n\\nConclusion'),
                       (CHANGES['article_id'], 'Editor introduction\n\n'+CHANGES['old']['fr']+'\n\nEditor conclusion')]
            for article_id, body in records:
                database.execute("INSERT INTO articles(id,slug,title,body,category,author,created_at,updated_at,image,status) "
                                 "VALUES (?,?,?,?,'Culture','Author','created','old-version','https://example.test/preserved.jpg','published')",
                                 (article_id, article_id, article_id, body))
            for locale in ('en', 'pt-BR', 'es'):
                database.execute("INSERT INTO translations VALUES (?,'article',?,'old-version',?,?,1,'created')",
                                 (locale, CHANGES['article_id'], locale, json.dumps({'body': CHANGES['old'][locale]})))
            module.apply(database, lambda query: query)
            module.apply(database, lambda query: query)
            legacy = database.execute('SELECT body,image,status,updated_at FROM articles WHERE id=?', (records[0][0],)).fetchone()
            self.assertEqual(legacy, ('Introduction\n\n## Heading\n\nConclusion', 'https://example.test/preserved.jpg', 'published', 'old-version'))
            current = database.execute('SELECT body,updated_at,image FROM articles WHERE id=?', (CHANGES['article_id'],)).fetchone()
            self.assertTrue(current[0].startswith('Editor introduction'))
            self.assertTrue(current[0].endswith('Editor conclusion'))
            self.assertIn(CHANGES['new']['fr'], current[0])
            self.assertEqual(current[2], 'https://example.test/preserved.jpg')
            self.assertEqual(database.execute('SELECT count(*) FROM revisions').fetchone()[0], 1)
            self.assertEqual(database.execute('SELECT count(*) FROM translations').fetchone()[0], 6)
            for locale in ('en', 'pt-BR', 'es'):
                row = database.execute('SELECT data FROM translations WHERE target_id=? AND version=? AND locale=?',
                                       (CHANGES['article_id'], current[1], locale)).fetchone()
                self.assertEqual(json.loads(row[0])['body'], CHANGES['new'][locale])
