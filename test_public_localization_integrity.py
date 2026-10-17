"""Public locale integrity checks for legacy content and client copy."""
import re
from html.parser import HTMLParser

import test_workflows as fixtures
from db import one, write
from localization import LOCALES, PHRASES, public_source_key


class PublicLocalizationIntegrityTests(fixtures.Fixture):
    def test_public_translation_source_attributes_are_opaque_and_localized(self):
        class CopyParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.current = None
                self.items = []

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if tag == "span" and attrs.get("data-source"):
                    self.current = [attrs["data-source"], ""]
                    self.items.append(self.current)

            def handle_data(self, data):
                if self.current is not None:
                    self.current[1] += data

            def handle_endtag(self, tag):
                if tag == "span":
                    self.current = None

        for locale, index in LOCALES.items():
            response = self.c.get(f"/{locale}/news")
            self.assertEqual(response.status_code, 200)
            parser = CopyParser()
            parser.feed(response.text)
            self.assertTrue(parser.items)
            for source_id, translated_text in parser.items:
                self.assertRegex(source_id, r"^k_[0-9a-f]{8}$")
                expected = next(
                    (values[index] for phrase, values in PHRASES.items()
                     if public_source_key(phrase) == source_id),
                    None,
                )
                self.assertIsNotNone(expected, source_id)
                self.assertEqual(translated_text, expected.strip())


    def test_public_creator_places_and_submission_copy_are_localized(self):
        expected = {
            "fr": {
                "place": ("Haïti · Canada", "Haïti · France"),
                "submit": "Vous connaissez un créateur à découvrir ? Partagez son nom, son origine et ses liens officiels.",
                "tagline": "Culture. Créativité. Impact.",
                "summary": "Créateurs haïtiens, culture et histoires. Haïti et sa diaspora.",
            },
            "en": {
                "place": ("Haiti · Canada", "Haiti · France"),
                "submit": "Know a creator we should discover? Share their name, origin, and official links.",
                "tagline": "Culture. Creativity. Impact.",
                "summary": "Haitian creators, culture and stories. Haiti and its diaspora.",
            },
            "pt-BR": {
                "place": ("Haiti · Canadá", "Haiti · França"),
                "submit": "Conhece um criador que deveríamos descobrir? Compartilhe seu nome, origem e links oficiais.",
                "tagline": "Cultura. Criatividade. Impacto.",
                "summary": "Criadores haitianos, nossa cultura e histórias. Haiti e sua diáspora.",
            },
            "es": {
                "place": ("Haití · Canadá", "Haití · Francia"),
                "submit": "¿Conoces a un creador que deberíamos descubrir? Comparte su nombre, origen y enlaces oficiales.",
                "tagline": "Cultura. Creatividad. Impacto.",
                "summary": "Creadores haitianos, nuestra cultura e historias. Haití y su diáspora.",
            },
        }
        for locale, copy in expected.items():
            for path in ("/", "/influencers"):
                page = self.c.get(f"/{locale}{path}")
                self.assertEqual(page.status_code, 200)
                for place in copy["place"]:
                    self.assertIn(place, page.text)
                self.assertNotIn("Ayiti ·", page.text)
            submit = self.c.get(f"/{locale}/submit-influencer")
            self.assertIn(copy["submit"], submit.text)
            home = self.c.get(f"/{locale}")
            self.assertIn(copy["tagline"], home.text)
            self.assertIn(copy["summary"], self.c.get(f"/{locale}/haiti").text)

    def test_public_section_summaries_are_localized(self):
        expected = {
            "fr": {
                "/world": "D’autres voix, d’autres cultures. La créativité à travers le monde.",
                "/trending": "Les articles les plus lus sur Geovyora au cours des sept derniers jours. Données de ce site uniquement.",
                "/interviews": "Des conversations sur les idées, l’expérience et le travail créatif.",
            },
            "en": {
                "/world": "Other voices, other cultures. Creativity around the world.",
                "/trending": "The most-read Geovyora stories over the past seven days. Data from this site only.",
                "/interviews": "Conversations about ideas, experience and creative work.",
            },
            "pt-BR": {
                "/world": "Outras vozes, outras culturas. Criatividade pelo mundo.",
                "/trending": "Os artigos mais lidos na Geovyora nos últimos sete dias. Dados apenas deste site.",
                "/interviews": "Conversas sobre ideias, experiências e trabalho criativo.",
            },
            "es": {
                "/world": "Otras voces, otras culturas. Creatividad en todo el mundo.",
                "/trending": "Los artículos más leídos de Geovyora en los últimos siete días. Datos de este sitio.",
                "/interviews": "Conversaciones sobre ideas, experiencias y trabajo creativo.",
            },
        }
        for locale, pages in expected.items():
            for path, phrase in pages.items():
                response = self.c.get(f"/{locale}{path}")
                self.assertEqual(response.status_code, 200)
                self.assertIn(phrase, response.text)


    def test_profile_language_field_hides_removed_locale(self):
        profile_id = "public-locale-profile-test"
        slug = "public-locale-profile-test"
        write(
            "INSERT INTO influencers(id,slug,name,username,origin,residence,category,bio,image,socials,languages,demo,status,created_at,updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (profile_id, slug, "Locale Test", "@locale-test", "Ayiti", "Kanada", "Kilti",
             "A verified test biography with enough detail.", "", "{}", "HT,fr,Kreyòl,English",
             0, "published", "2026-01-01T00:00:00+00:00", "2026-01-01T00:00:00+00:00"),
        )
        try:
            response = self.c.get(f"/fr/influencer/{slug}")
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("Kreyòl", response.text)
            self.assertNotIn("HT,", response.text)
            self.assertIn("fr, English", response.text)
        finally:
            write("DELETE FROM influencers WHERE id=?", (profile_id,))

    def test_legacy_article_image_credits_use_french_text(self):
        expected = {
            "geovyora-wilson-isidor-2026":
                "Timmy96 / Wikimedia Commons — CC0 1.0 (photo non modifiée)",
            "geovyora-khaby-lame-ai-twin-2026":
                "Sam Barnes / Web Summit via Sportsfile — CC BY 4.0 (photo non modifiée)",
        }
        for article_id, credit in expected.items():
            row = one("SELECT image_credit FROM articles WHERE id=?", (article_id,))
            self.assertIsNotNone(row)
            self.assertEqual(row["image_credit"], credit)
            article = one("SELECT slug FROM articles WHERE id=?", (article_id,))
            response = self.c.get(f"/fr/article/{article['slug']}")
            self.assertEqual(response.status_code, 200)
            self.assertIn(credit, response.text)
            self.assertNotRegex(response.text, r"(?i)foto a pa modifye")
