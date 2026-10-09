# Geovyora — sa ou bezwen fè manyèlman

Geovyora deja anliy sou `https://geovyora.com`. Lis sa a konsène koneksyon sèvis ki poko verifye; li pa mande pou kreye yon dezyèm sit oswa ranplase baz done pwodiksyon an. Atik Ariana Lafond lan ak foto li dwe rete nan baz done pwodiksyon aktyèl la.

1. Si w ap itilize Render, verifye web service, worker ak baz done ki deja sèvi sit live la anvan ou fè chanjman. Pa enpòte blueprint la kòm yon nouvo stack si objektif la se mete ajou sèvis ki egziste deja yo. Mete `SITE_URL=https://geovyora.com` sou web ak worker.
2. Ranpli gwoup anviwònman `vyora-services` yon sèl fwa. Web ak worker pataje li. Mete kle Mux, Google Translation, Firebase ak S3 ki nan `.env.example`. Kite bucket soumisyon an prive. Pa mete kle yo nan Git.
3. Nan shell web la: `python manage.py create-admin`. Chwazi imel, non ak modpas ou; pa gen modpas pa defo. Antre nan `/admin`.
4. Ranpli non responsab biznis la, kontak, adrès ak tèks legal yo nan CMS. Yon modèl legal pa yon validasyon legal. Ajoute vrè atik, pwofil, sous, foto ak videyo ou gen dwa itilize. Deplwaman pwodiksyon pa ajoute demonstrasyon yo.
5. Nan Mux, mete webhook HTTPS `/api/webhooks/mux`; nan Firebase, aktive pwojè web/push ak VAPID; nan Google, aktive Translation ak limit depans; nan S3, mete CORS ak règleman bucket apwopriye. Teste yon vrè upload, tradiksyon ak notifikasyon apre koneksyon.
6. AdSense: mande apwobasyon epi konfigire yon CMP sètifye kote obligatwa. Script piblisite a poko aktive nan kòd la. Entegrasyon CMP ak AdSense rete travay apre ou chwazi founisè a ak jwenn apwobasyon.
7. Newsletter: koleksyon ak dezabònman pare. Voye kanpay imel mande yon founisè imel, domèn ekspeditè valide ak entegrasyon livrezon; sa poko fèt.
8. Aktive sovgad otomatik hosting lan, monitoring ak politik konsèvasyon done/foto prive. Teste restorasyon. Zouti lokal ki anba yo deja pare, men yo pa otomatikman aktive sovgad hosting ou.

## Verifikasyon san revele kle yo

`python operations.py check`

Rapò a montre sèlman true/false. Li verifye prezans konfigirasyon yo; li pa teste kont oswa apwobasyon sèvis ekstèn yo.

## Sovgad ak restorasyon

`python operations.py backup backups/vyora-2026-10-03.sqlite3`

Avèk `DATABASE_URL`, menm kòmand lan kreye yon archive PostgreSQL; sèvi ak ekstansyon `.dump`. Li bezwen `pg_dump` sou machin k ap fè sovgad la. Kenbe backup yo prive ak chifre nan depo sovgad ou. Fichye ki deja egziste pa janm ranplase.

`python operations.py restore-sqlite backups/vyora-2026-10-03.sqlite3 data/restored.sqlite3`

Restore SQLite fèt sou yon nouvo fichye sèlman. Pou PostgreSQL, sèvi ak `pg_restore` sou yon nouvo bazdone tès epi verifye li anvan yon restorasyon pwodiksyon.
