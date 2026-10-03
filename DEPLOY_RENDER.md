# Geovyora — Render

1. Mete kòd pwojè a nan rasin repo GitHub Ezechias22/geovyora. main.py, Dockerfile, render.yaml ak requirements.txt dwe nan menm rasin lan. Pa ajoute .env, JSON kont sèvis, bazdone oswa backup.
2. Nan Render, New → Blueprint, konekte repo a epi branch main. Modèl la kreye geovyora-web, geovyora-worker, geovyora-db ak gwoup geovyora-services. Tout compute plans yo peye; verifye montan Render montre avan Apply. PostgreSQL la sèvi ak 1 GB disk epi aksè ekstèn dezaktive; sèvis Render yo sèvi ak koneksyon entèn.
3. Apre kreyasyon, Environment Groups → geovyora-services: ajoute SITE_URL ak URL HTTPS Render bay sèvis web la. Mete MUX_TOKEN_ID, MUX_TOKEN_SECRET, FIREBASE_PUBLIC_CONFIG, FIREBASE_VAPID_KEY, FIREBASE_SERVICE_ACCOUNT, S3_ACCESS_KEY_ID ak S3_SECRET_ACCESS_KEY. Gwoup la deja gen endpoint ak non bucket B2 yo. Konfigirasyon JSON sou Render dwe JSON brit sou yon liy san apostwòf ki antoure li nan .env. Pa enpòte .env antye: DATABASE_URL, COOKIE_SECURE ak SEED_DEMO soti nan blueprint la; pa sèvi ak valè lokal yo.
4. Save/redeploy tou de sèvis yo. Nan web Shell: python manage.py create-admin. Kont ak kontni bazdone lokal yo pa transfere otomatikman. Pa gen seed demo nan pwodiksyon.
5. Kreye webhook Mux pou https://URL-RENDER/api/webhooks/mux; mete signing secret nan MUX_WEBHOOK_SECRET nan gwoup la, epi redeploy. Kle Data la pa kle API videyo.
6. Ajoute URL HTTPS egzak Render la nan allowedOrigins CORS bucket piblik la ansanm ak localhost pou tès. Pa ajoute /ht oswa lòt path nan origin.
7. Google Translation ka rete san kle. Lè billing/API prepare, ajoute GOOGLE_TRANSLATION_KEY nan gwoup la. AdSense/CMP ak imel newsletter toujou gen etap entegrasyon apa.
8. Teste login, foto piblik ak foto soumisyon prive, videyo Mux, webhook ak notifikasyon Firebase. Verifye /health. Aktive backup hosting ak monitoring. Zouti operations.py backup pou PostgreSQL bezwen pg_dump enstale sou machin k ap fè backup la.

Modèl la verifye kont dokiman Render aktyèl yo; sèvis yo pa kreye oswa teste live nan sesyon sa a. Gwoup anviwònman an pa itilize sync:false. Kle prive yo ajoute nan dashboard la sèlman.
