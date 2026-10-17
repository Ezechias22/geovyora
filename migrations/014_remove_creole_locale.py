"""Remove Haitian Creole as a public locale while preserving other-language content."""
import json


def apply(connection, sql):
    # Articles written in Creole become French originals when a verified French
    # translation exists. Otherwise archive them so Creole text cannot surface
    # under a French URL. Keep every underlying record for editorial recovery.
    articles=connection.execute(sql("SELECT * FROM articles WHERE lower(locale)='ht' OR lower(locale) LIKE 'ht-%'")).fetchall()
    for row in articles:
        article=dict(row);version=article.get('updated_at') or article.get('created_at') or ''
        translated=connection.execute(sql("SELECT data FROM translations WHERE target_type='article' AND target_id=? AND version=? AND locale='fr'"),(article['id'],version)).fetchone()
        if translated:
            data=json.loads(translated['data'])
            connection.execute(sql("UPDATE articles SET title=?,subtitle=?,body=?,locale='fr' WHERE id=?"),(data.get('title',article['title']),data.get('subtitle',article['subtitle']),data.get('body',article['body']),article['id']))
        else:
            connection.execute(sql("UPDATE articles SET status='archived',locale='fr' WHERE id=?"),(article['id'],))

    # Influencer biographies used the Creole source as their implicit locale.
    # Use a stored French translation when available; otherwise keep the record
    # private from public listings until an editor rewrites the biography.
    influencers=connection.execute(sql("SELECT * FROM influencers")).fetchall()
    for row in influencers:
        influencer=dict(row);version=influencer.get('updated_at') or influencer.get('created_at') or ''
        translated=connection.execute(sql("SELECT data FROM translations WHERE target_type='influencer' AND target_id=? AND version=? AND locale='fr'"),(influencer['id'],version)).fetchone()
        languages=[]
        for code in (influencer.get('languages') or '').split(','):
            code=code.strip()
            if code and code.split('-')[0].lower()!='ht':languages.append(code)
        if translated:
            data=json.loads(translated['data'])
            connection.execute(sql("UPDATE influencers SET bio=?,languages=? WHERE id=?"),(data.get('bio',influencer['bio']),','.join(languages),influencer['id']))
        else:
            connection.execute(sql("UPDATE influencers SET status='archived',languages=? WHERE id=?"),(','.join(languages),influencer['id']))

    # Videos do not have localized text caches, so archive old-language videos.
    connection.execute(sql("UPDATE videos SET status='archived',locale='fr' WHERE lower(locale)='ht' OR lower(locale) LIKE 'ht-%'"))
    connection.execute(sql("UPDATE push_subscriptions SET locale='fr' WHERE lower(locale)='ht' OR lower(locale) LIKE 'ht-%'"))
    connection.execute(sql("UPDATE newsletter_subscribers SET locale='fr' WHERE lower(locale)='ht' OR lower(locale) LIKE 'ht-%'"))

    # Stop pending Creole-language campaigns from being delivered after the
    # locale is removed. Sent campaigns remain in the record for audit history.
    connection.execute(sql("UPDATE deliveries SET status='cancelled' WHERE status='queued' AND campaign_id IN (SELECT id FROM campaigns WHERE lower(locale)='ht' OR lower(locale) LIKE 'ht-%')"))
    connection.execute(sql("UPDATE campaigns SET status=CASE WHEN status IN ('draft','scheduled','queued') THEN 'cancelled' ELSE status END,locale='fr',url=replace(url,'/ht/','/fr/') WHERE lower(locale)='ht' OR lower(locale) LIKE 'ht-%'"))
    connection.execute(sql("UPDATE ad_placements SET active=0,locale='fr' WHERE lower(locale)='ht' OR lower(locale) LIKE 'ht-%'"))

    connection.execute(sql("DELETE FROM seo_metadata WHERE lower(locale)='ht' OR lower(locale) LIKE 'ht-%'"))
    connection.execute(sql("DELETE FROM translation_jobs WHERE lower(locale)='ht' OR lower(locale) LIKE 'ht-%'"))
    connection.execute(sql("DELETE FROM translations WHERE lower(locale)='ht' OR lower(locale) LIKE 'ht-%'"))
    connection.execute(sql("DELETE FROM supported_languages WHERE lower(code)='ht' OR lower(code) LIKE 'ht-%'"))
    connection.execute(sql("INSERT INTO settings(key,value) VALUES ('default_locale','fr') ON CONFLICT(key) DO UPDATE SET value='fr'"))
    connection.execute(sql("UPDATE settings SET value='Culture. Créativité. Impact.' WHERE key='tagline' AND value='Kilti. Kreyativite. Enpak.'"))
