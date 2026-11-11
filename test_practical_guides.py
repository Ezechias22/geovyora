"""Publication, localization and preservation of practical editorial guides."""
import html
import importlib.util
import json
import sqlite3
from pathlib import Path

import test_workflows as fixtures
from db import rows,write
from i18n import labels
from practical_tools import COPY

ROOT=Path(__file__).parent
GUIDES=json.loads((ROOT/'editorial/news/2026-11-10-practical-guides.json').read_text())

class PracticalGuides(fixtures.Fixture):
    def test_guides_have_complete_text_tools_and_sources_in_four_languages(self):
        for locale in ('fr','en','pt-BR','es'):
            archive=self.c.get('/'+locale+'/guides')
            self.assertEqual(archive.status_code,200)
            self.assertIn(labels(locale)['guides_summary'],html.unescape(archive.text))
            for guide in GUIDES:
                text=guide if locale=='fr' else guide['translations'][locale]
                response=self.c.get('/'+locale+'/article/'+guide['slug'])
                rendered=html.unescape(response.text)
                self.assertEqual(response.status_code,200)
                self.assertIn('<h1>'+text['title']+'</h1>',rendered)
                self.assertIn(text['body'].split('\n\n')[0],rendered)
                self.assertIn(text['body'].split('\n\n')[-1],rendered)
                self.assertIn(COPY[locale]['privacy'],rendered)
                self.assertIn(COPY[locale][guide['tool']+'_title'],rendered)
                self.assertIn('data-tool="'+guide['tool']+'"',rendered)
                self.assertIn('/static/practical-tools.js?v=20261110',rendered)
                self.assertNotIn('translation-note',rendered)
                self.assertIn('/'+locale+'/article/'+guide['slug'],archive.text)
                for source in guide['sources']:self.assertIn(source,rendered)
            home=self.c.get('/'+locale)
            self.assertIn('/'+locale+'/guides',home.text)
            for guide in GUIDES:
                text=guide if locale=='fr' else guide['translations'][locale]
                self.assertIn(text['title'],html.unescape(home.text))
            sitemap=self.c.get('/sitemap.xml').text
            self.assertIn('/'+locale+'/guides</loc>',sitemap)

    def test_tool_script_is_not_loaded_for_other_articles_or_contact(self):
        for path in ('/fr/contact','/fr/article/haiti-insecurite-campagnes-proteger-civils'):
            text=self.c.get(path).text
            self.assertNotIn('/static/practical-tools.js',text)
            self.assertNotIn('data-tool=',text)

    def test_no_published_guides_means_no_guide_menu_and_noindex_archive(self):
        previous=rows("SELECT id,status FROM articles WHERE kind='guide'")
        try:
            write("UPDATE articles SET status='draft' WHERE kind='guide'")
            self.assertNotIn('/fr/guides',self.c.get('/fr').text)
            self.assertIn('content="noindex',self.c.get('/fr/guides').text)
            self.assertNotIn('/fr/guides</loc>',self.c.get('/sitemap.xml').text)
        finally:
            for record in previous:write('UPDATE articles SET status=? WHERE id=?',(record['status'],record['id']))

    def test_publication_is_atomic_and_never_replaces_existing_editorial_work(self):
        spec=importlib.util.spec_from_file_location('practical_guides',ROOT/'migrations/026_practical_editorial_guides.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with sqlite3.connect(':memory:') as db:
            db.executescript((ROOT/'migrations/001_initial.sql').read_text())
            db.execute('CREATE TABLE categories(id TEXT PRIMARY KEY,name TEXT UNIQUE,slug TEXT UNIQUE,sort_order INTEGER,active INTEGER)')
            module.apply(db,lambda q:q)
            self.assertEqual(db.execute("SELECT count(*) FROM articles WHERE status='published' AND kind='guide'").fetchone()[0],2)
            self.assertEqual(db.execute('SELECT count(*) FROM translations').fetchone()[0],6)
            db.execute("UPDATE articles SET body='Owner revision',status='deleted' WHERE id=?",(GUIDES[0]['id'],))
            module.apply(db,lambda q:q)
            self.assertEqual(db.execute('SELECT body,status FROM articles WHERE id=?',(GUIDES[0]['id'],)).fetchone(),('Owner revision','deleted'))
            self.assertEqual(db.execute('SELECT count(*) FROM translations').fetchone()[0],6)
