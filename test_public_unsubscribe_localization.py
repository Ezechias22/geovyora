import unittest

from localization import ui_text


class PublicUnsubscribeLocalizationTests(unittest.TestCase):
    def test_private_unsubscribe_label_is_localized_for_every_supported_locale(self):
        expected = {
            "fr": "Lien privé de désabonnement",
            "en": "Private unsubscribe link",
            "pt-BR": "Link privado para cancelar inscrição",
            "es": "Enlace privado para cancelar suscripción",
        }

        for locale, translation in expected.items():
            with self.subTest(locale=locale):
                self.assertEqual(ui_text("Lyen prive dezabònman", locale), translation)
