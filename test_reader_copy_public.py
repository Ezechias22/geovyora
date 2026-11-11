"""Professional public wording retains articles and honest illustration captions."""
import html
import json
from pathlib import Path
import test_workflows as fixtures
from db import rows
from editorial_policy import POLICIES

CHANGES=json.loads((Path(__file__).parent/'editorial/audit/2026-11-10-reader-copy-changes.json').read_text())

class ReaderCopyPublic(fixtures.Fixture):
    def test_reader_copy_is_applied_in_every_language_without_losing_articles(self):
        for change in CHANGES:
            article=rows('SELECT slug,status FROM articles WHERE id=?',(change['article_id'],))[0]
            self.assertEqual(article['status'],'published')
            for locale,edit in change['locales'].items():
                text=html.unescape(self.c.get('/'+locale+'/article/'+article['slug']).text)
                self.assertIn(edit['new'],text)
                self.assertNotIn(edit['old'],text)
                self.assertNotIn('translation-note',text)
        response=self.c.get('/fr/article/khaby-lame-jimo-dijital-ako-975-milyon')
        self.assertEqual(response.status_code,200)
        self.assertIn('975',response.text)

    def test_policy_keeps_synthetic_image_safeguards_without_preparation_boilerplate(self):
        for locale,policy in POLICIES.items():
            text=html.unescape(self.c.get('/'+locale+'/editorial').text)
            self.assertEqual(self.c.get('/'+locale+'/editorial').status_code,200)
            self.assertIn(policy['sections'][3][0],text)
            self.assertNotIn('AI tools may assist',text)
            self.assertNotIn('Les outils d’IA peuvent aider',text)
            self.assertIn('Ezechias Toussaint',text)
