"""Regression checks for translated public accessibility labels."""
import test_workflows as fixtures
from db import one


class PublicAccessibleLabelsTests(fixtures.Fixture):
    def test_accessible_labels_are_localized_on_public_article_pages(self):
        article = one("SELECT slug FROM articles WHERE slug='wilson-isidor-deklarasyon-ayiti-repiblik-dominikenn'")
        self.assertIsNotNone(article)
        expected = {
            'fr': ('Navigation principale', 'Fermer', 'Trier les commentaires', 'Trier'),
            'en': ('Main navigation', 'Close', 'Sort comments', 'Sort'),
            'pt-BR': ('Navegação principal', 'Fechar', 'Ordenar comentários', 'Ordenar'),
            'es': ('Navegación principal', 'Cerrar', 'Ordenar comentarios', 'Ordenar'),
        }
        for locale, labels in expected.items():
            response = self.c.get('/' + locale + '/article/' + article['slug'])
            self.assertEqual(response.status_code, 200)
            for label in labels[:3]:
                self.assertIn('aria-label="' + label + '"', response.text)
            for creole in ('Navigasyon prensipal', 'Fèmen', 'Tri kòmantè'):
                self.assertNotIn('aria-label="' + creole + '"', response.text)
            creators = self.c.get('/' + locale + '/influencers')
            self.assertEqual(creators.status_code, 200)
            self.assertIn('aria-label="' + labels[3] + '"', creators.text)
            self.assertNotIn('aria-label="Tri"', creators.text)
