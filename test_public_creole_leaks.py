"""Focused regression tests for public localization and category links."""
import unittest
import test_workflows as fixtures
from db import one


class PublicCreoleFixTests(fixtures.Fixture):
    def test_public_localization_has_no_creole_badges_or_french_tagline(self):
        from localization import localize_html
        html = '<span>Tradiksyon editoryal · </span><b>Rédaction Geovyora</b><i>Culture. Créativité. Impact.</i>'
        expected = {
            'en': ('Editorial translation ·', 'Geovyora Editorial Team', 'Culture. Creativity. Impact.'),
            'pt-BR': ('Tradução editorial ·', 'Equipe editorial Geovyora', 'Cultura. Criatividade. Impacto.'),
            'es': ('Traducción editorial ·', 'Equipo editorial de Geovyora', 'Cultura. Creatividad. Impacto.'),
        }
        for locale, phrases in expected.items():
            rendered = localize_html(html, locale)
            for phrase in phrases:
                self.assertIn(phrase, rendered)
            self.assertNotIn('Tradiksyon editoryal', rendered)

    def test_public_category_filter_uses_non_creole_id_and_keeps_filtering(self):
        category = one("SELECT id,name FROM categories WHERE name='Espò' AND active=1")
        self.assertIsNotNone(category)
        listing = self.c.get('/en/news')
        self.assertEqual(listing.status_code, 200)
        self.assertIn('href="?category=' + category['id'] + '"', listing.text)
        self.assertNotIn('category=Esp%C3%B2', listing.text)
        self.assertNotIn('>Espò<', listing.text)
        filtered = self.c.get('/en/news', params={'category': category['id']})
        self.assertEqual(filtered.status_code, 200)
        self.assertIn('Wilson Isidor', filtered.text)
