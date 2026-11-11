"""Regression checks for complete, version-safe public article translations."""
import html
import importlib.util
import json
import sqlite3
from pathlib import Path

import test_workflows as fixtures
from db import write

ROOT = Path(__file__).parent
COPY_EDITS = json.loads((ROOT / 'editorial/audit/2026-11-10-reader-copy-changes.json').read_text())
PACKAGES = ('2026-11-02.json', '2026-11-02-suite.json', '2026-11-02-bresil.json')
ARTICLES = sum([json.loads((ROOT / 'editorial/news' / name).read_text()) for name in PACKAGES], [])
TRANSLATIONS = {locale: json.loads((ROOT / 'editorial/translations' / (locale+'.json')).read_text())
                for locale in ('en', 'pt-BR', 'es')}


class ArticleTranslations(fixtures.Fixture):
    def test_all_nine_articles_have_complete_localized_pages_and_metadata(self):
        sitemap = self.c.get('/sitemap.xml').text
        for article in ARTICLES:
            for locale in ('fr', 'en', 'pt-BR', 'es'):
                expected = article if locale == 'fr' else TRANSLATIONS[locale][article['id']]
                expected = dict(expected)
                for edit in COPY_EDITS:
                    if edit['article_id'] == article['id'] and edit.get('field','body') == 'body':
                        copy = edit['locales'][locale]
                        expected['body'] = expected['body'].replace(copy['old'],copy['new'],1)
                with self.subTest(article=article['slug'], locale=locale):
                    response = self.c.get('/'+locale+'/article/'+article['slug'])
                    self.assertEqual(response.status_code, 200)
                    rendered = html.unescape(response.text)
                    self.assertIn('<h1>'+expected['title']+'</h1>', rendered)
                    self.assertIn(expected['body'].split('\n\n')[0], rendered)
                    self.assertIn(expected['body'].split('\n\n')[-1], rendered)
                    self.assertIn('id="translated-body" lang="'+locale+'"', rendered)
                    self.assertIn('name="description" content="'+expected['subtitle']+'"', rendered)
                    self.assertIn('"inLanguage": "'+locale+'"', rendered)
                    self.assertIn('/'+locale+'/article/'+article['slug'], sitemap)
                    for phrase in ('Atik sa a disponib an', 'Tradiksyon editoryal', 'Koreksyon editoryal'):
                        self.assertNotIn(phrase, rendered)
                    for source in article['sources']:
                        self.assertIn(source, rendered)
                    if locale != 'fr':
                        self.assertNotIn('translation-note', rendered)
                        self.assertEqual(len(expected['body'].split('\n\n')), len(article['body'].split('\n\n')))

    def test_missing_translation_notice_uses_the_page_language(self):
        article_id = 'fallback-notice-test'
        write('INSERT INTO articles(id,slug,title,body,category,author,created_at,updated_at,publish_at,status) '
              "VALUES (?,?,'Titre français','Texte français.','Société','Geovyora','test','test','2026-11-02T00:00:00+00:00','published')",
              (article_id, article_id))
        try:
            expected = {'en': 'This article is available in French.',
                        'pt-BR': 'Este artigo está disponível em francês.',
                        'es': 'Este artículo está disponible en francés.'}
            for locale, message in expected.items():
                rendered = html.unescape(self.c.get('/'+locale+'/article/'+article_id).text)
                self.assertIn(message, rendered)
                self.assertNotIn('Atik sa a', rendered)
                self.assertIn('id="translated-body" lang="fr"', rendered)
        finally:
            write('DELETE FROM page_views WHERE article_id=?', (article_id,))
            write('DELETE FROM articles WHERE id=?', (article_id,))

    def test_translation_migration_preserves_edits_and_rejects_changed_sources(self):
        spec = importlib.util.spec_from_file_location('complete_translations', ROOT / 'migrations/021_complete_news_translations.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for factory in (None, sqlite3.Row):
            with self.subTest(row_factory=factory), sqlite3.connect(':memory:') as database:
                database.row_factory = factory
                database.executescript((ROOT / 'migrations/001_initial.sql').read_text())
                for index, article in enumerate(ARTICLES[:2]):
                    body = article['body'] if index == 0 else article['body']+'\n\nA new editorial fact.'
                    database.execute('INSERT INTO articles(id,slug,title,subtitle,body,category,author,created_at,updated_at) '
                                     "VALUES (?,?,?,?,?,'Société','Geovyora','test','production-version')",
                                     (article['id'], article['slug'], article['title'], article['subtitle'], body))
                database.execute("INSERT INTO translations VALUES ('existing','article',?,'production-version','en',?,1,'test')",
                                 (ARTICLES[0]['id'], json.dumps({'title': 'Existing editorial title'})))
                module.apply(database, lambda query: query)
                module.apply(database, lambda query: query)
                count = database.execute('SELECT count(*) FROM translations').fetchone()[0]
                self.assertEqual(count, 3)
                existing = database.execute("SELECT data FROM translations WHERE id='existing'").fetchone()[0]
                self.assertEqual(json.loads(existing), {'title': 'Existing editorial title'})
                stale = database.execute('SELECT count(*) FROM translations WHERE target_id=?', (ARTICLES[1]['id'],)).fetchone()[0]
                self.assertEqual(stale, 0)
                version = database.execute("SELECT version FROM translations WHERE locale='pt-BR'").fetchone()[0]
                self.assertEqual(version, 'production-version')
