"""The World page is the complete public catalog, with real pagination."""
import html
import importlib.util
import json
import re
import sqlite3
import uuid
from pathlib import Path
from unittest.mock import patch

import test_workflows as fixtures
from db import rows, write

ROOT = Path(__file__).parent
ARTICLES = json.loads((ROOT / 'editorial/news/2026-11-02-expansion.json').read_text())


def links(markup, locale='fr'):
    return set(re.findall('/'+locale+r'/article/([^"?<>]+)', html.unescape(markup)))


class WorldCatalog(fixtures.Fixture):
    def test_world_exposes_all_public_articles_in_every_language(self):
        with patch.dict('os.environ', {'ALLOW_DEMO_CONTENT': '0'}):
            expected = {r['slug'] for r in rows("SELECT slug FROM articles WHERE status='published' AND demo=0")}
            self.assertGreaterEqual(len(expected), 20)
            for locale in ('fr', 'en', 'pt-BR', 'es'):
                found = set()
                for page in range(1, (len(expected)+23)//24+1):
                    response = self.c.get('/'+locale+'/world', params={'page': page})
                    self.assertEqual(response.status_code, 200)
                    current = links(response.text, locale)
                    self.assertFalse(found & current)
                    found |= current
                self.assertEqual(found, expected, locale)
            # The Haïti page keeps its regional scope.
            regional = links(self.c.get('/fr/haiti').text)
            allowed = {r['slug'] for r in rows("SELECT slug FROM articles WHERE status='published' AND demo=0 AND region='haiti'")}
            self.assertTrue(regional <= allowed)
            self.assertNotIn('recife-recnplay-2026-creativite-technologie', regional)

    def test_world_pagination_does_not_link_to_an_empty_page(self):
        identifiers = []
        with patch.dict('os.environ', {'ALLOW_DEMO_CONTENT': '0'}):
            count = len(rows("SELECT id FROM articles WHERE status='published' AND demo=0"))
            try:
                for index in range(max(0, 24-count)+1):
                    identifier = 'catalog-test-'+uuid.uuid4().hex
                    identifiers.append(identifier)
                    write("INSERT INTO articles(id,slug,title,body,category,author,status,created_at,updated_at,publish_at) "
                          "VALUES (?,?,?,'Catalog test body.','Société','Geovyora','published','test','test','2026-11-02')",
                          (identifier, identifier, identifier))
                    if index == max(0, 24-count)-1:
                        self.assertNotIn('?page=2', self.c.get('/fr/world').text)
                first = self.c.get('/fr/world')
                self.assertIn('?page=2', first.text)
                second = self.c.get('/fr/world?page=2')
                self.assertEqual(len(links(first.text)), 24)
                self.assertFalse(links(first.text) & links(second.text))
                self.assertNotIn('?page=3', second.text)
                self.assertTrue(links(second.text))
            finally:
                for identifier in identifiers:
                    write('DELETE FROM articles WHERE id=?', (identifier,))

    def test_world_category_filter_still_works_across_regions(self):
        category_id = 'catalog-category-'+uuid.uuid4().hex
        identifiers = []
        write('INSERT INTO categories(id,name,slug) VALUES (?,?,?)', (category_id, category_id, category_id))
        try:
            for region, status in [('haiti', 'published'), ('world', 'published'), ('international', 'draft'), ('world', 'deleted')]:
                identifier = 'catalog-filter-'+uuid.uuid4().hex
                identifiers.append(identifier)
                write("INSERT INTO articles(id,slug,title,body,category,author,region,status,created_at,updated_at,publish_at) "
                      "VALUES (?,?,?,'Catalog test body.',?,'Geovyora',?,?,'test','test','2026-11-02')",
                      (identifier, identifier, identifier, category_id, region, status))
            response = self.c.get('/fr/world', params={'category': category_id})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(links(response.text), set(identifiers[:2]))
        finally:
            for identifier in identifiers:
                write('DELETE FROM articles WHERE id=?', (identifier,))
            write('DELETE FROM categories WHERE id=?', (category_id,))

    def test_five_new_articles_have_complete_translations_and_sources(self):
        sitemap = self.c.get('/sitemap.xml').text
        for article in ARTICLES:
            for locale in ('fr', 'en', 'pt-BR', 'es'):
                expected = article if locale == 'fr' else article['translations'][locale]
                with self.subTest(article=article['slug'], locale=locale):
                    response = self.c.get('/'+locale+'/article/'+article['slug'])
                    self.assertEqual(response.status_code, 200)
                    rendered = html.unescape(response.text)
                    self.assertIn('<h1>'+expected['title']+'</h1>', rendered)
                    self.assertIn(expected['body'].split('\n\n')[0], rendered)
                    self.assertIn(expected['body'].split('\n\n')[-1], rendered)
                    self.assertIn('id="translated-body" lang="'+locale+'"', rendered)
                    self.assertIn('/'+locale+'/article/'+article['slug'], sitemap)
                    self.assertNotIn('translation-note', rendered)
                    for source in article['sources']:
                        self.assertIn(source, rendered)

    def test_publication_is_repeatable_and_preserves_editorial_changes(self):
        spec = importlib.util.spec_from_file_location('five_multilingual_articles', ROOT / 'migrations/024_publish_five_multilingual_articles.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with sqlite3.connect(':memory:') as database:
            database.executescript((ROOT / 'migrations/001_initial.sql').read_text())
            database.execute('CREATE TABLE categories(id TEXT PRIMARY KEY,name TEXT UNIQUE,slug TEXT UNIQUE,sort_order INTEGER,active INTEGER)')
            module.apply(database, lambda query: query)
            self.assertEqual(database.execute('SELECT count(*) FROM articles').fetchone()[0], 5)
            self.assertEqual(database.execute('SELECT count(*) FROM translations').fetchone()[0], 15)
            database.execute("UPDATE articles SET body='Owner edit',status='deleted' WHERE id=?", (ARTICLES[0]['id'],))
            database.execute("UPDATE translations SET data=? WHERE target_id=? AND locale='en'", (json.dumps({'title': 'Owner translation'}), ARTICLES[0]['id']))
            module.apply(database, lambda query: query)
            self.assertEqual(database.execute('SELECT count(*) FROM articles').fetchone()[0], 5)
            self.assertEqual(database.execute('SELECT count(*) FROM translations').fetchone()[0], 15)
            self.assertEqual(database.execute('SELECT body,status FROM articles WHERE id=?', (ARTICLES[0]['id'],)).fetchone(), ('Owner edit', 'deleted'))
            translated = database.execute("SELECT data FROM translations WHERE target_id=? AND locale='en'", (ARTICLES[0]['id'],)).fetchone()[0]
            self.assertEqual(json.loads(translated)['title'], 'Owner translation')
