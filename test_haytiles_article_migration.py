import json
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MIGRATION = ROOT / "migrations" / "016_haytiles_ezechias_article.sql"
SCHEMA = """
CREATE TABLE articles (
    id TEXT PRIMARY KEY, slug TEXT UNIQUE NOT NULL, title TEXT NOT NULL,
    subtitle TEXT NOT NULL DEFAULT '', body TEXT NOT NULL, category TEXT NOT NULL,
    region TEXT NOT NULL DEFAULT 'haiti', kind TEXT NOT NULL DEFAULT 'article',
    image TEXT NOT NULL DEFAULT '', image_credit TEXT NOT NULL DEFAULT '',
    author TEXT NOT NULL, locale TEXT NOT NULL DEFAULT 'fr', status TEXT NOT NULL DEFAULT 'draft',
    featured INTEGER NOT NULL DEFAULT 0, demo INTEGER NOT NULL DEFAULT 0,
    sponsored INTEGER NOT NULL DEFAULT 0, publish_at TEXT, created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL, sources TEXT NOT NULL DEFAULT '', tags TEXT NOT NULL DEFAULT ''
);
CREATE TABLE translations (
    id TEXT PRIMARY KEY, target_type TEXT NOT NULL, target_id TEXT NOT NULL,
    version TEXT NOT NULL, locale TEXT NOT NULL, data TEXT NOT NULL,
    manual INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL,
    UNIQUE(target_type, target_id, version, locale)
);
"""


class HaytilesArticleMigrationTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(SCHEMA)

    def tearDown(self):
        self.connection.close()

    def test_publishes_sourced_article_with_all_active_translations(self):
        self.apply_migration()
        article = self.connection.execute(
            "SELECT * FROM articles WHERE id = ?", ("geovyora-haytiles-2026",)
        ).fetchone()
        self.assertIsNotNone(article)
        self.assertEqual(article["status"], "published")
        self.assertEqual(article["locale"], "fr")
        self.assertEqual(article["category"], "Teknoloji")
        self.assertEqual(article["region"], "haiti")
        self.assertEqual(article["author"], "Ezechias Toussaint")
        self.assertEqual(article["sponsored"], 0)
        self.assertIn("haytiles.com", article["sources"])
        self.assertIn("play.google.com", article["sources"])
        self.assertIn("IA", article["image_credit"])

        translations = self.connection.execute(
            "SELECT locale, data, manual FROM translations "
            "WHERE target_type = 'article' AND target_id = ? ORDER BY locale",
            ("geovyora-haytiles-2026",),
        ).fetchall()
        self.assertEqual({row["locale"] for row in translations}, {"en", "es", "pt-BR"})
        for row in translations:
            self.assertEqual(row["manual"], 1)
            content = json.loads(row["data"])
            self.assertTrue(content["title"])
            self.assertGreater(len(content["body"]), 1500)
            self.assertTrue(content["image_credit"])

    def apply_migration(self):
        script = MIGRATION.read_text(encoding="utf-8")
        self.assertEqual(script.count(";"), 4, "Unexpected semicolon inside a SQL value")
        for statement in script.split(";"):
            if statement.strip():
                self.connection.execute(statement)

    def test_migration_is_idempotent(self):
        self.apply_migration()
        self.apply_migration()
        self.assertEqual(
            self.connection.execute("SELECT COUNT(*) FROM articles WHERE id = 'geovyora-haytiles-2026'").fetchone()[0],
            1,
        )
        self.assertEqual(
            self.connection.execute("SELECT COUNT(*) FROM translations WHERE target_id = 'geovyora-haytiles-2026'").fetchone()[0],
            3,
        )


if __name__ == "__main__":
    unittest.main()
