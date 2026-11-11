"""Editorial additions must remain versioned, reversible and multilingual."""
import html
import importlib.util
import json
import sqlite3
import unittest
from pathlib import Path
import test_workflows as fixtures
from db import rows

ROOT=Path(__file__).parent
PACKAGE=json.loads((ROOT/'editorial/reporting/2026-11-10-content-review.json').read_text())

class ReportingPublic(fixtures.Fixture):
    def test_reviewed_articles_have_complete_localized_revisions(self):
        for change in PACKAGE:
            for locale,expected in change['expected'].items():
                with self.subTest(article=change['article_id'],locale=locale):
                    response=self.c.get('/'+locale+'/article/'+change['slug'])
                    text=html.unescape(response.text)
                    self.assertEqual(response.status_code,200)
                    self.assertIn('<h1>'+expected['title']+'</h1>',text)
                    self.assertIn(expected['body'].split('\n\n')[0],text)
                    self.assertIn(expected['body'].split('\n\n')[-1],text)
                    for patch in change['locales'][locale]:
                        if patch['field']=='body':
                            for block in patch['new'].split('\n\n'):
                                if block and not block.startswith('## '):self.assertIn(block,text)
                    self.assertNotIn('translation-note',text)
                    if change['notes']:self.assertIn(change['notes'][locale],text)
        self.assertGreaterEqual(len(rows("SELECT id FROM articles WHERE status='published' AND demo=0")),22)

    def test_audience_claims_are_withdrawn_without_changing_media(self):
        for locale in ('fr','en','pt-BR','es'):
            text=html.unescape(self.c.get('/'+locale+'/article/ariana-lafond-tiktok-scene-internationale').text)
            self.assertNotIn('18,4',text);self.assertNotIn('18.4',text)
            self.assertNotIn('332,5',text);self.assertNotIn('332.5',text)
            image=rows("SELECT image FROM articles WHERE id='geovyora-ariana-2026-editorial'")[0]['image']
            if image:self.assertIn(image,text)
            self.assertIn('House of Challenge',text)

class ReportingMigration(unittest.TestCase):
    def test_unrelated_owner_edits_and_old_translations_are_preserved(self):
        spec=importlib.util.spec_from_file_location('review',ROOT/'migrations/028_editorial_reporting_review.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        change=PACKAGE[0];stamp='old-version'
        originals={}
        for locale,edits in change['locales'].items():
            data=dict(change['expected'][locale])
            if locale=='fr':data['sources']=change['sources_after']
            for edit in reversed(edits):
                field=edit['field']
                # Restore the source citation explicitly because its replacement is empty.
                if field=='sources' and not edit['new']:data[field]=data.get(field,'')+edit['old']
                else:data[field]=data[field].replace(edit['new'],edit['old'],1)
            originals[locale]=data
        with sqlite3.connect(':memory:') as db:
            db.executescript((ROOT/'migrations/001_initial.sql').read_text())
            fr=originals['fr'];fr['body']+='\n\nOwner note outside the edited passages.'
            db.execute("INSERT INTO articles(id,slug,title,subtitle,body,category,author,locale,status,image,publish_at,created_at,updated_at,sources) VALUES (?,?,?,?,?,'Culture','Geovyora','fr','published','owner-photo','original-date',?,?,?)",(change['article_id'],change['slug'],fr['title'],fr['subtitle'],fr['body'],stamp,stamp,fr.get('sources','')))
            for locale in ('en','pt-BR','es'):
                db.execute("INSERT INTO translations VALUES (?,'article',?,?,?,?,1,?)",(locale,change['article_id'],stamp,locale,json.dumps(originals[locale]),stamp))
            module.apply(db,lambda q:q)
            record=db.execute('SELECT body,publish_at,image,updated_at,status FROM articles').fetchone()
            self.assertTrue(record[0].endswith('Owner note outside the edited passages.'))
            self.assertEqual(record[1:3],('original-date','owner-photo'))
            self.assertEqual(record[4],'published');self.assertNotEqual(record[3],stamp)
            self.assertEqual(db.execute('SELECT count(*) FROM translations').fetchone()[0],6)
            self.assertEqual(db.execute('SELECT count(*) FROM revisions').fetchone()[0],1)
            module.apply(db,lambda q:q)
            self.assertEqual(db.execute('SELECT count(*) FROM revisions').fetchone()[0],1)
            self.assertEqual(db.execute('SELECT count(*) FROM translations').fetchone()[0],6)

    def test_edit_guard_rejects_changed_passages_without_mutating_input(self):
        spec=importlib.util.spec_from_file_location('review_guard',ROOT/'migrations/028_editorial_reporting_review.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        data={'body':'Owner changed this paragraph.'}
        result=module.revise(data,[{'field':'body','old':'Expected text','new':'Replacement'}])
        self.assertIsNone(result)
        self.assertEqual(data,{'body':'Owner changed this paragraph.'})
