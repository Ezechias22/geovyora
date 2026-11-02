"""Publication and preservation checks for the source-backed news package."""
import importlib.util
import json
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).parent


class HaitiNews(unittest.TestCase):
    def test_migration_publishes_and_preserves_existing_editorial_changes(self):
        self.verify_package('017_haiti_news_20261102.py', '2026-11-02.json')

    def test_additional_articles_publish_with_correct_regions_and_preserve_edits(self):
        self.verify_package('018_more_news_20261102.py', '2026-11-02-suite.json')

    def test_rumor_clarification_preserves_other_edits_and_is_repeatable(self):
        spec = importlib.util.spec_from_file_location('rumor_clarification', ROOT / 'migrations/019_clarify_florida_rumor.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with sqlite3.connect(':memory:') as database:
            database.execute('CREATE TABLE articles(id TEXT PRIMARY KEY,body TEXT,updated_at TEXT)')
            body = 'Existing editorial introduction\n\n'+module.OLD+'\n\nExisting editorial conclusion'
            database.execute('INSERT INTO articles VALUES (?,?,?)', ('geovyora-floride-learjet-20261102', body, 'previous'))
            module.apply(database, lambda query: query)
            expected = body.replace(module.OLD, module.NEW, 1)
            first = database.execute('SELECT body,updated_at FROM articles').fetchone()
            self.assertEqual(first[0], expected)
            self.assertNotEqual(first[1], 'previous')
            module.apply(database, lambda query: query)
            self.assertEqual(database.execute('SELECT body,updated_at FROM articles').fetchone(), first)

    def verify_package(self, migration, package):
        spec = importlib.util.spec_from_file_location('haiti_news_migration', ROOT / 'migrations' / migration)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        articles = json.loads((ROOT / 'editorial/news' / package).read_text())
        with sqlite3.connect(':memory:') as database:
            database.executescript((ROOT / 'migrations/001_initial.sql').read_text())
            database.execute('CREATE TABLE categories(id TEXT PRIMARY KEY,name TEXT UNIQUE,slug TEXT UNIQUE,sort_order INTEGER,active INTEGER)')
            module.apply(database, lambda query: query)
            self.assertEqual(database.execute("SELECT count(*) FROM articles WHERE status='published' AND demo=0 AND locale='fr'").fetchone()[0], 3)
            for article in articles:
                stored = database.execute('SELECT body,sources,region FROM articles WHERE id=?', (article['id'],)).fetchone()
                self.assertEqual(stored[0], article['body'])
                self.assertEqual(stored[1].splitlines(), article['sources'])
                self.assertEqual(stored[2], article.get('region', 'haiti'))
            database.execute("UPDATE articles SET body='Editorial correction',status='archived' WHERE id=?", (articles[0]['id'],))
            module.apply(database, lambda query: query)
            self.assertEqual(database.execute('SELECT count(*) FROM articles').fetchone()[0], 3)
            self.assertEqual(database.execute('SELECT body,status FROM articles WHERE id=?', (articles[0]['id'],)).fetchone(), ('Editorial correction', 'archived'))
