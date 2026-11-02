"""Import the supplied guides as drafts, without replacing existing content."""
import argparse
from datetime import datetime, timezone
from pathlib import Path

from db import connection, migrate, sql

ROOT = Path(__file__).parent
DRAFTS = (
    ('01-verifier-une-annonce.md', 'verifier-une-annonce-avant-de-partager',
     'Une méthode pour retrouver les sources, distinguer annonce et confirmation, et éviter les erreurs de contexte.'),
    ('02-partenariat-createur.md', 'createurs-marques-clarifier-un-partenariat',
     'Travail demandé, droits de réutilisation, paiement et transparence : les points à discuter avant un accord.'),
    ('03-traduire-pour-la-diaspora.md', 'publier-pour-la-diaspora-traduction-et-contexte',
     'Dates, devises, conditions locales et corrections : rendre une information compréhensible dans plusieurs langues.'),
)


def import_drafts():
    migrate()
    stamp = datetime.now(timezone.utc).isoformat()
    with connection() as database:
        for filename, slug, subtitle in DRAFTS:
            text = (ROOT / 'editorial' / 'drafts' / filename).read_text(encoding='utf-8')
            title, preparation_note, body = text.split('\n\n', 2)
            if not title.startswith('# ') or not preparation_note.startswith('Statut : brouillon'):
                raise ValueError('Invalid draft format: '+filename)
            result = database.execute(sql(
                "INSERT INTO articles(id,slug,title,subtitle,body,category,region,author,locale,status,created_at,updated_at) "
                "VALUES (?,?,?,?,?,'Teknoloji','world','Geovyora','fr','draft',?,?) ON CONFLICT DO NOTHING"
            ), ('geovyora-guide-'+slug, slug, title[2:], subtitle,
                body.strip()+'\n\nNote de préparation : texte rédigé avec une assistance IA, à relire avant publication.', stamp, stamp))
            print(('Imported draft: ' if result.rowcount else 'Preserved existing record: ')+slug)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Import into the configured database; never publishes.')
    args = parser.parse_args()
    if args.apply:
        import_drafts()
    else:
        print('No database changed. Use --apply to import 3 drafts into the configured database.')
