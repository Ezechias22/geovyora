"""Verified owner contact, localized context and canonical discovery paths."""
import html
import importlib.util
import sqlite3
from pathlib import Path

import test_workflows as fixtures
from db import one, write
from i18n import labels


class PublisherContact(fixtures.Fixture):
    def test_owner_supplied_contact_is_public_in_every_language(self):
        self.assertEqual(one("SELECT value FROM settings WHERE key='contact_person'")['value'], 'Ezechias Toussaint')
        self.assertEqual(one("SELECT value FROM settings WHERE key='contact_email'")['value'], 'contact@haytiles.com')
        for locale in ('fr', 'en', 'pt-BR', 'es'):
            for page in ('contact', 'about', 'editorial', 'privacy', 'copyright', 'terms'):
                response = self.c.get('/'+locale+'/'+page)
                self.assertEqual(response.status_code, 200)
                text = html.unescape(response.text)
                self.assertIn('Ezechias Toussaint', text)
                self.assertIn(labels(locale)['public_contact_person'], text)
                self.assertIn('href="mailto:contact@haytiles.com"', text)

    def test_contact_can_be_edited_by_admin_after_the_migration(self):
        client, csrf = self.login()
        response = client.post('/admin/settings/save', data={'csrf_token': csrf, 'contact_person': 'Updated contact'})
        try:
            self.assertEqual(response.status_code, 200)
            self.assertIn('Updated contact', self.c.get('/fr/contact').text)
        finally:
            write("UPDATE settings SET value='Ezechias Toussaint' WHERE key='contact_person'")

    def test_rankings_redirect_preserves_query_and_uses_translated_destination(self):
        for locale in ('fr', 'en', 'pt-BR', 'es'):
            response = self.c.get('/'+locale+'/rankings?category=example&page=2', follow_redirects=False)
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response.headers['location'], '/'+locale+'/trending?category=example&page=2')

    def test_article_dates_and_context_are_localized_without_rewriting_content(self):
        slug = 'bresil-elections-2026-audits-urnes-4-novembre'
        for locale in ('fr', 'en', 'pt-BR', 'es'):
            response = self.c.get('/'+locale+'/article/'+slug)
            self.assertIn(labels(locale)['documentary_context'], html.unescape(response.text))
            self.assertIn(labels(locale)['published_on'], html.unescape(response.text))
            self.assertIn('<time datetime=', response.text)
            self.assertIn('/'+locale+'/editorial', response.text)
            self.assertNotIn('translation-note', response.text)

    def test_sitemap_includes_publisher_policies_and_excludes_empty_archives(self):
        text = self.c.get('/sitemap.xml').text
        for locale in ('fr', 'en', 'pt-BR', 'es'):
            for page in ('about', 'contact', 'editorial', 'privacy', 'terms', 'copyright'):
                self.assertIn('/'+locale+'/'+page+'</loc>', text)
            for page in ('interviews', 'discoveries', 'videos', 'rankings'):
                self.assertNotIn('/'+locale+'/'+page+'</loc>', text)

    def test_contact_migration_runs_once_and_preserves_company_and_address(self):
        path = Path(__file__).parent / 'migrations/025_public_publisher_contact.py'
        spec = importlib.util.spec_from_file_location('contact_migration', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with sqlite3.connect(':memory:') as db:
            db.execute('CREATE TABLE settings(key TEXT PRIMARY KEY,value TEXT)')
            db.executemany('INSERT INTO settings VALUES (?,?)', [('contact_company', 'Existing company'), ('contact_address', 'Existing address')])
            module.apply(db, lambda q: q)
            data = dict(db.execute('SELECT key,value FROM settings'))
            self.assertEqual(data['contact_person'], 'Ezechias Toussaint')
            self.assertEqual(data['contact_email'], 'contact@haytiles.com')
            self.assertEqual(data['contact_company'], 'Existing company')
            self.assertEqual(data['contact_address'], 'Existing address')
