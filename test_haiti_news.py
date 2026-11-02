"""Publication and preservation checks for the source-backed news package."""
import importlib.util
import json
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).parent


class HaitiNews(unittest.TestCase):
    def test_migration_publishes_and_preserves_existing_editorial_changes(self):
        spec = importlib.util.spec_from_file_location('haiti_news_migration', ROOT / 'migrations' / '017_haiti_news_20261102.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        articles = json.loads((ROOT / 'editorial/news/2026-11-02.json').read_text())
        with sqlite3.connect(':memory:') as database:
            database.executescript((ROOT / 'migrations/001_initial.sql').read_text())
            database.execute('CREATE TABLE categories(id TEXT PRIMARY KEY,name TEXT UNIQUE,slug TEXT UNIQUE,sort_order INTEGER,active INTEGER)')
            module.apply(database, lambda query: query)
            self.assertEqual(database.execute("SELECT count(*) FROM articles WHERE status='published' AND demo=0 AND locale='fr'").fetchone()[0], 3)
            for article in articles:
                stored = database.execute('SELECT body,sources FROM articles WHERE id=?', (article['id'],)).fetchone()
                self.assertEqual(stored[0], article['body'])
                self.assertEqual(stored[1].splitlines(), article['sources'])
            database.execute("UPDATE articles SET body='Editorial correction',status='archived' WHERE id=?", (articles[0]['id'],))
            module.apply(database, lambda query: query)
            self.assertEqual(database.execute('SELECT count(*) FROM articles').fetchone()[0], 3)
            self.assertEqual(database.execute('SELECT body,status FROM articles WHERE id=?', (articles[0]['id'],)).fetchone(), ('Editorial correction', 'archived'))
