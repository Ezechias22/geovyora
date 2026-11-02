"""Seller authorization must work before ad serving is enabled."""
import os
from unittest.mock import patch

import test_workflows as fixtures
from db import one, write


class AdsReadiness(fixtures.Fixture):
    def test_ads_txt_authorizes_verified_publisher_without_enabling_ads(self):
        previous = {key: one('SELECT value FROM settings WHERE key=?', (key,))
                    for key in ('publisher_id', 'ads_enabled')}
        try:
            for key, value in [('publisher_id', ''), ('ads_enabled', '0')]:
                write('INSERT INTO settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value', (key, value))
            with patch.dict(os.environ, {'ADSENSE_PUBLISHER_ID': 'pub-2023569258267325'}):
                response = self.c.get('/ads.txt')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.text, 'google.com, pub-2023569258267325, DIRECT, f08c47fec0942fa0\n')
                self.assertTrue(response.headers['content-type'].startswith('text/plain'))
                home = self.c.get('/fr').text
                self.assertIn('client=ca-pub-2023569258267325', home)
                self.assertNotIn('class="adsbygoogle"', home)
            write("UPDATE settings SET value='pub-1234567890' WHERE key='publisher_id'")
            self.assertIn('google.com, pub-1234567890, DIRECT', self.c.get('/ads.txt').text)
            self.assertIn('client=ca-pub-1234567890', self.c.get('/fr').text)
            write("UPDATE settings SET value='invalid, injected seller' WHERE key='publisher_id'")
            self.assertEqual(self.c.get('/ads.txt').status_code, 404)
            self.assertNotIn('adsbygoogle.js', self.c.get('/fr').text)
        finally:
            for key, record in previous.items():
                if record:
                    write('UPDATE settings SET value=? WHERE key=?', (record['value'], key))
                else:
                    write('DELETE FROM settings WHERE key=?', (key,))

    def test_editorial_method_has_localized_title_and_correction_path(self):
        titles = {'fr': 'Notre méthode éditoriale', 'en': 'Our editorial method',
                  'pt-BR': 'Nosso método editorial', 'es': 'Nuestro método editorial'}
        for locale, title in titles.items():
            response = self.c.get('/'+locale+'/editorial')
            self.assertEqual(response.status_code, 200)
            self.assertIn(title, response.text)
            self.assertIn('/'+locale+'/contact?kind=correction', response.text)
            self.assertNotIn('Règleman editoryal', response.text)
