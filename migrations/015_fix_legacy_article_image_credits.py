"""Restore localized image credits after retiring the legacy locale."""
import json


ARTICLE_IDS = {
    "geovyora-wilson-isidor-2026":
        "Timmy96 / Wikimedia Commons — CC0 1.0 (photo non modifiée)",
    "geovyora-khaby-lame-ai-twin-2026":
        "Sam Barnes / Web Summit via Sportsfile — CC BY 4.0 (photo non modifiée)",
}


def apply(connection, sql):
    for article_id, fallback in ARTICLE_IDS.items():
        article = connection.execute(
            sql("SELECT updated_at FROM articles WHERE id=?"), (article_id,)
        ).fetchone()
        if not article:
            continue

        translation = connection.execute(
            sql("SELECT data FROM translations WHERE target_type='article' "
                "AND target_id=? AND version=? AND locale='fr'"),
            (article_id, article["updated_at"]),
        ).fetchone()
        credit = fallback
        if translation:
            data = json.loads(translation["data"])
            candidate = str(data.get("image_credit", "")).strip()
            if candidate and "foto a pa modifye" not in candidate.casefold():
                credit = candidate
        connection.execute(
            sql("UPDATE articles SET image_credit=? WHERE id=?"),
            (credit, article_id),
        )
