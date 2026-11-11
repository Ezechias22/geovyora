"""Reader-copy cleanup preserves versions, factual content and media credits."""
import importlib.util
import json
import sqlite3
import unittest
from pathlib import Path

ROOT=Path(__file__).parent
CHANGES=json.loads((ROOT/'editorial/audit/2026-11-10-reader-copy-changes.json').read_text())

class ReaderCopyMigration(unittest.TestCase):
    def test_cleanup_preserves_images_dates_status_and_edited_translations(self):
        spec=importlib.util.spec_from_file_location('reader_copy',ROOT/'migrations/027_reader_facing_copy.py')
        migration=importlib.util.module_from_spec(spec);spec.loader.exec_module(migration)
        change=CHANGES[0];old='original-version'
        with sqlite3.connect(':memory:') as db:
            db.executescript((ROOT/'migrations/001_initial.sql').read_text())
            body='Facts unchanged. '+change['locales']['fr']['old']
            db.execute("INSERT INTO articles(id,slug,title,body,category,author,status,image,image_credit,publish_at,created_at,updated_at) VALUES (?,?,?,?,'Teknoloji','Geovyora','published','original-photo','Synthetic illustration','original-publication',?,?)",
                       (change['article_id'],'guide','Guide',body,old,old))
            for locale in ('en','pt-BR','es'):
                text='Owner-edited text' if locale=='es' else 'Facts unchanged. '+change['locales'][locale]['old']
                db.execute("INSERT INTO translations VALUES (?,'article',?,?,?,?,1,?)",(locale,change['article_id'],old,locale,json.dumps({'title':'Guide','body':text}),old))
            migration.apply(db,lambda q:q)
            record=db.execute('SELECT body,updated_at,publish_at,image,image_credit,status FROM articles').fetchone()
            self.assertEqual(record[0],'Facts unchanged. '+change['locales']['fr']['new'])
            self.assertNotEqual(record[1],old)
            self.assertEqual(record[2:],('original-publication','original-photo','Synthetic illustration','published'))
            current=dict(db.execute('SELECT locale,data FROM translations WHERE version=?',(record[1],)))
            self.assertEqual(len(current),3)
            self.assertEqual(json.loads(current['es'])['body'],'Owner-edited text')
            self.assertIn(change['locales']['en']['new'],json.loads(current['en'])['body'])
            self.assertEqual(db.execute('SELECT count(*) FROM translations').fetchone()[0],6)
            self.assertEqual(json.loads(db.execute('SELECT data FROM revisions').fetchone()[0])['body'],body)
            migration.apply(db,lambda q:q)
            self.assertEqual(db.execute('SELECT count(*) FROM revisions').fetchone()[0],1)
            self.assertEqual(db.execute('SELECT count(*) FROM translations').fetchone()[0],6)
