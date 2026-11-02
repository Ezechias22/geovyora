"""Clarify the reader-reported rumor while preserving other editorial changes."""
from datetime import datetime, timezone

OLD = 'La thèse d’une bombe, évoquée dans des messages que des lecteurs peuvent rencontrer, n’est pas établie par cette déclaration. Cela ne revient pas à annoncer que chaque hypothèse a été définitivement écartée : cela signifie que le document consulté ne fournit pas cette preuve. À ce stade, une formule affirmative sur un attentat dépasserait les informations vérifiées pour cet article.'
NEW = 'Une rumeur selon laquelle il s’agirait d’une bombe a été signalée à Geovyora par un lecteur. Nous n’en avons pas établi l’origine ni l’ampleur de diffusion. La déclaration de la FAA consultée ne confirme pas cette affirmation et ne détermine pas la cause de l’accident. Cela ne signifie pas que toutes les hypothèses ont été définitivement écartées : cela signifie qu’à ce stade, présenter une bombe ou un attentat comme un fait dépasserait les éléments vérifiés pour cet article.'


def apply(connection, sql):
    record = connection.execute(sql('SELECT body FROM articles WHERE id=?'), ('geovyora-floride-learjet-20261102',)).fetchone()
    if not record:
        return
    body = record['body'] if hasattr(record, 'keys') else record[0]
    if OLD in body:
        connection.execute(sql('UPDATE articles SET body=?,updated_at=? WHERE id=? AND body=?'),
                           (body.replace(OLD, NEW, 1), datetime.now(timezone.utc).isoformat(),
                            'geovyora-floride-learjet-20261102', body))
