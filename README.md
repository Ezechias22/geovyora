# Geovyora — sit medya sou kreyatè

Vèsyon 2 · Sit web sèlman · Dark mode sèlman · Ayiti, dyaspora ak mond lan.

Sa a se menm pwojè Geovyora a, avèk CMS, administrasyon, baz done pèsistan ak fonksyon piblik yo elaji. Pa gen kont lektè, aplikasyon mobil, 2FA, marketplace oswa chat prive. Non Geovyora a se yon chwa kreyatif; disponibilite mak/domèn li poko verifye.

## Lanse sou Windows

1. Enstale Python 3.12 oswa pi resan.
2. Dekonprese ZIP la.
3. Double-klike **START_WINDOWS.bat**.
4. Kreye premye admin lan lè script la mande w sa. Pa gen modpas default.
5. Sit: `http://localhost:8000` · Admin: `http://localhost:8000/admin`.

Script la lanse worker la nan yon dezyèm fenèt pou tradiksyon ak planifikasyon. Fèmen toude fenèt yo pou sispann sit la. Premye enstalasyon depandans yo bezwen entènèt.

## Lanse sou Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py create-admin --email YOUR_EMAIL --name YOUR_NAME
uvicorn main:app --host 127.0.0.1 --port 8000
```

Nan yon dezyèm terminal, aktive menm environment lan epi kouri `python worker.py`. Ranpli `.env` avèk kle ou bezwen yo; pa pataje fichye sa a. Dat planifikasyon admin yo sèvi ak UTC.

## Fonksyon piblik

- Dakèy magazin, Ayiti, Mond, aktyalite, entèvyou, videyo, tandans sou sit la, dekouvèt, anyè ak pwofil medya.
- Gwo nouvèl an vedèt chwazi nan CMS; lòd seksyon dakèy configurable.
- Kategori aktif configurable; filtè anyè pa kategori, peyi rezidans ak platfòm; tri resan/A–Z; rechèch ki tolere aksan.
- Atik ki rann sou sèvè: foto prensipal, otè, dat, sous, tags, kontni patwone/demo ak tan lekti.
- Kontni rich san HTML lib: tit, paragraf, sitasyon, foto/lejand, lyen HTTPS ak videyo Mux ki pare.
- Atik sove lokalman, kopi lyen, pataj natif, WhatsApp, atik asosye ak istwa koreksyon editoryal piblik.
- Pwofil medya editoryal ak orijin/rezidans separe, bio, rezo ofisyèl, atik asosye ak estatistik separe pa platfòm. Chak chif antre manyèlman bezwen yon sous ak yon dat; pa gen total moun inik envante ni verifikasyon otomatik sous la.
- Kòmantè san kont, repons nan thread, likes, tri/pagination, rapò, modifye/retire sèlman avèk cookie navigatè ki ekri a. Non/pseudo pa idantite verifye.
- Tout kòmantè pase nan moderasyon. Entèdiksyon limite yon cookie tanporèman (1–168 èdtan), avèk rezon ak retire limit; pa gen entèdiksyon an mas sou IP.
- Fòm kreyatè, enfòmasyon, kontak, piblisite, koreksyon ak retrè. Foto soumisyon opsyonèl rete nan yon bucket prive, twa foto maksimòm, 10 MB chak, validasyon fòma/dimansyon.
- Notification preferences, abònman/dezabònman san kont, preferans enfliyansè sou menm navigatè a.
- Newsletter opsyonèl san kont: konsantman, enskripsyon, lyen prive dezabònman ak konfimasyon POST. Livrezon imel poko konekte.
- Paj enfòmasyon/politik yo gen tèks pwovizwa ki dwe adapte ak enfòmasyon antrepriz la anvan lansman.

## Administrasyon

Modil: Apèsi, Atik/Entèvyou, Enfliyansè, Videyo/Mux, Medya, Kòmantè, Rapò, Soumisyon, Tradiksyon, Kategori, Tags, SEO, Newsletter, Notifikasyon, Piblisite, Analitik, Ekip, Paramèt, Kont ekip la ak Jounal aksyon.

- CMS: draft, in_review, scheduled, published, archived, preview prive, vèsyon ak restore.
- Modération: approve/reject/hide/delete, revizyon rapò ak soumisyon, rezon ak audit log. Kantite rapò pa efase kontni otomatikman.
- Ekip: kreye manm, chanje wòl, dezaktive/reactive, reset modpas, revoke sesyon. Chak manm ka chanje pwòp modpas li avèk modpas aktyèl la. Super Admin pwoteje nan UI pou evite bloke dènye mèt la.
- Wòl sou backend: super_admin, admin, editor, moderator. Editè soumèt atik pou revizyon; li pa pibliye ni modifye paramèt sit la.
- SEO pa atik/pwofil ak lang: title, description, noindex, canonical, hreflang sèlman pou tradiksyon ki egziste, sitemap ak Article JSON-LD sou atik reyèl.
- Redirections lè slug atik chanje. Drafts, previews, demo ak paj entèn pa indexe.
- Paramèt: non mak, tagline, kontak antrepriz, lang default, lòd seksyon, limit tradiksyon, frekans push ak paramèt piblisite.
- Kategori yo ka chanje non san kraze kategori atik/pwofil ki deja itilize non sa a. Tags jere nan admin; atik yo toujou sèvi ak yon lis tags separe pa vigil.

### Fòma kontni rich

```text
## Tit seksyon

Yon paragraf ak yon [lyen](https://example.org).

> Yon sitasyon

![Lejand foto](https://example.org/photo.jpg)

[video:slug-videyo-ki-pare]
```

HTML, scripts ak embeds lib pa egzekite nan kò atik la. Vidyo embedded yo bezwen yon slug Mux ki deja ready.

## Lang ak tradiksyon

- Navigasyon ak prensipal tèks UI gen diksyonè HT, FR, EN, PT-BR, ES. Preferans: lyen/chwa lang, cookie, lang navigatè, default.
- `/` detekte variant tankou pt-BR oswa es-MX, epi respekte lang URL yo.
- Lòt lang soti nan lis Google Translation reyèl la: **Admin → Tradiksyon → Mete lis lang Google yo ajou**. Lis la gen yon rechèch nan header. Pa gen lis "tout lang sou tè a" envante.
- RTL sipòte pou lang tankou Arab ak Ebre. Lang siplemantè sèvi ak labels anglè jiskaske tradiksyon UI a pare.
- Tradiksyon atik, bio, kòmantè ak UI pase nan yon fil travay pèsistan ak deduplikasyon pa kontni/vèsyon/lang, cache, retries limite ak yon limit reyèl karaktè pa mwa.
- Worker prepare senk lang prensipal yo pou atik ki pibliye; lòt lang sou demann. Kòmantè tradui sèlman lè lektè a mande sa.
- Tradiksyon UI fèt sèlman sou tèks interface ki nan kòd la, pa sou non/pseudo ni done moun antre nan fòm yo.
- Tradiksyon editoryal pa ranplase otomatikman. Lè sous la chanje, vèsyon tradiksyon anvan yo rete konsève; nouvo vèsyon an bezwen nouvo tradiksyon.
- Lè pa gen kle, limit rive oswa sèvis echwe, orijinal la toujou lizib. Gen kèk tèks/politik ki rete an Kreyòl san sèvis tradiksyon; paj politik yo make sa.
- Demann ki echwe kapab konsome rezèv bidjè a: limit la rete konservatif. Tès avèk provider simile pase; sèvis reyèl la poko teste san kle.

## Notifikasyon

- Firebase mande pèmisyon sèlman apre bouton itilizatè a. Subscription mare ak cookie prive, lang, sijè ak enfliyansè.
- Admin kreye draft oswa planifye kanpay UTC, preview lyen, mete nan fil oswa anile.
- Worker filtre selon lang, sijè oswa kreyatè, respekte limit pa navigatè pa 24 èdtan, epi travay an batch san plafon 500 destinatè pa kanpay.
- Chak livrezon gen claim atomik pou evite doublon. Livrezon ensèten apre crash/network pa retried otomatikman; yo make pou revizyon. Sa favorize evite double push, epi li ka mande yon revizyon manyèl pou mesaj ki pa konfime.
- Invalid tokens retire. Dezabònman an anile livrezon queued ak opt-in repons kòmantè yo.
- Push repons kòmantè sèlman apre apwobasyon yon repons, pou pwopriyetè parent la ki te opt-in epi ki toujou abòne. Chak repons kreye yon kanpay yon sèl fwa. Pa gen push pou chak like.
- Kontni kanpay la antre nan lang admin chwazi a; li pa tradui an tout lang otomatikman. Mesaj repons yo gen kopi nan senk lang prensipal yo, anglè fallback pou lòt yo.

## Medya ak piblisite

- Mux: direct upload, uploading/processing/ready/error, player, webhooks HMAC timestamp ak event deduplication. Se sèlman ready ki disponib piblikman.
- Foto CMS: presigned POST nan S3-compatible storage, JPEG/PNG/WebP, 10 MB. Endpoint verifye bytes reyèl, fòma, dimansyon, foto anime ak fichye domaje anvan make ready.
- Foto soumisyon: validasyon avan upload nan PRIVATE_SUBMISSION_BUCKET. Fichye yo pa gen URL piblik; sèlman staff otorize resevwa yon lyen download tanporè 120 segonn.
- Piblisite dirèk: bannè make Publicité, lang configurable, activate/deactivate. Pa parèt sou paj demo.
- AdSense: publisher/ad-slot settings ak ads.txt prepare. **Script AdSense toujou pa aktive**: apwobasyon Google, yon CMP apwopriye/sètifye kote obligatwa, consent tests ak validasyon lang kò paj la rete obligatwa. Pa gen ads sou kontni Kreyòl, admin, drafts oswa demo. Pa gen revni pwomèt.

## Kle sèvis yo

Gade `.env.example`:

| Sèvis | Configuration |
|---|---|
| Database pwodiksyon | DATABASE_URL PostgreSQL |
| HTTPS | SITE_URL=https://... ; COOKIE_SECURE=1 |
| Mux | MUX_TOKEN_ID, MUX_TOKEN_SECRET, MUX_WEBHOOK_SECRET |
| Google Translation Basic v2 | GOOGLE_TRANSLATION_KEY (server-only, restrict key) |
| Firebase | FIREBASE_PUBLIC_CONFIG JSON, FIREBASE_VAPID_KEY, FIREBASE_SERVICE_ACCOUNT secret JSON |
| Foto CMS S3 | S3_ENDPOINT_URL si nesesè, S3_REGION, S3_BUCKET, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, MEDIA_PUBLIC_URL |
| Foto soumisyon prive | PRIVATE_SUBMISSION_BUCKET, ak bucket policy ki pa piblik |

Webhook Mux: `SITE_URL/api/webhooks/mux`. Mete CORS storage pou origin HTTPS sit la. Sèvi ak kle ki gen sèlman dwa bucket nesesè yo; pa mete okenn kle nan browser oswa depo Git.

Limit MAX_VIDEO_BYTES kontwole UI anvan upload URL kreye. Mux URL la ale dirèk nan sèvis la: fè limit provider-side tou. Chunked upload/retry avanse, signed playback ak jesyon subtitle editoryal pa aplike nan UI sa a; Mux Player sèvi ak subtitles asset la genyen.

## Hosting san Cloudflare

Pa gen Cloudflare nan pwojè sa a. Geovyora deja anliy sou `https://geovyora.com`. Atik Ariana Lafond lan ak foto li se kontni pwodiksyon; konsève yo lè w ap deplwaye sou baz done ki deja sèvi sit la. `render.yaml` se yon modèl pou kreye yon nouvo stack, li pa metòd pou modifye sit pwodiksyon an; verifye sèvis ak baz done ki egziste deja yo anvan ou enpòte li.

- **Docker lokal**: `cp .env.example .env` epi `docker compose up --build`. PostgreSQL pèsistan ak worker. Admin: `docker compose exec web python manage.py create-admin`. Modpas DB nan compose se pou dev sèlman; ranplase li pou pwodiksyon.
- **Render**: `render.yaml` prepare web, worker ak PostgreSQL. Enpòte depo Git/blueprint ou sou kont pa ou, ranpli SITE_URL, kle sèvis, epi konfigire menm kle ki nesesè nan worker la. Modèl la itilize plan peye pou evite sèvis dòmi; verifye plan/tarif yo anvan aktive.
- **VPS / hosting Docker**: reverse proxy HTTPS, database PostgreSQL, web + worker. Pa konte sou disk efemè pou done pwodiksyon.

Stack: FastAPI + Jinja SSR + JavaScript/CSS, SQLite dev / PostgreSQL prod, jobs nan database + worker Python. Pa gen Next.js, Redis oswa Celery nan livrezon sa a. Search eskane jiska 5 000 atik nan V1; pou pi gwo katalòg, pase nan full-text index PostgreSQL. Analitik rete debaz: lekti deduplike pa atik/navigatè/jou ak filtre bot senp, pa yon measurè rezo sosyal ni anti-fraud konplè.

## Sekirite ak operasyon

- Modpas scrypt; sesyon HttpOnly; CSRF ak origin checks; templates escaped; URL/format validation; rate limits database; limit body/chunked requests; ownership cookies; audit logs.
- Migrations ak initial seeding serialize pou worker/web pa aplike menm travay an menm tan.
- `/health` verifye database. Logs pa dwe gen kle; pa aktive debug HTTP ki ekspoze kle Google nan URL.
- Setup/reset staff atravè console prive; pa gen default password ni password reset imel nan V1.
- Rate limits sèvi ak adrès peer; reverse proxy dwe pase adrès vizitè sèlman atravè yon chain proxy ou fè konfyans. IP pataje ka afekte plizyè moun; pa gen fingerprinting.
- SQLite backup: itilize backup API konsistan, pa kopi database pandan WAL ap ekri. PostgreSQL: pg_dump/backup hosting, chifreman, epi teste restore sou yon lòt baz. Volume pèsistan pa yon backup.
- Ajoute monitoring, politik konsèvasyon ak suppression done selon operasyon ou. Pyès jointes prive ki pa asosye ak yon soumisyon bezwen yon janitor/retention policy nan hosting lan; li pa otomatikman aplike isit la.

```bash
python manage.py reset-password --email YOUR_EMAIL
python manage.py disable-staff --email STAFF_EMAIL
python manage.py migrate
python -m unittest discover -v
```

## Tès fèt

**15 gwoup tès entegrasyon pase**, avèk database tanporè:

- Paj piblik, 5 lang, deteksyon lang, 404.
- Draft pa piblik, private preview, publish/search/revisions.
- Kòmantè pending/approval/reply/ownership, likes, report deduplication.
- Permissions, CSRF, cross-origin, signature Mux, webhook deduplication.
- Scheduled publishing yon sèl fwa.
- Kategori/tags/SEO/noindex ak nouvo modil admin.
- Translation queue dedup, budget blocking, cache, manual correction pa overwrite.
- Push lang/sijè targeting, frequency deferral, unsubscribe, one-time enqueue.
- Reply push explicit consent, private audience, one event, unsubscribe cancellation.
- Metrics ak source/date, anonymous bans, team/session revocation.
- Newsletter consent/private unsubscribe; accent search; RTL markup.
- Image bytes validation ak mocked storage; submission attachment ownership; rich content parser; oversized request rejection.

**QA Chromium**: sove atik, voye kontak, login admin, kreye kategori ak kanpay draft, meni mobil. Desktop 1440px; mobil 390px. Home, anyè, atik, kontak, admin, kategori, tags, SEO, notifikasyon, tradiksyon, newsletter, ekip ak kont ekip la teste san overflow horizontal ni erè JavaScript.

**Poko teste live**: PostgreSQL/Docker/Render, uploads Mux/S3 reyèl, Firebase push reyèl, Google Translation reyèl, AdSense/CMP, imèl newsletter, gwo chaj ak load testing. Tès ekstèn yo itilize doubles/mocks kote endike. Sa pa vle di sèvis yo konekte.

Tout atik/pwofil demo yo fiktif epi make. Imaj studio a se yon illustration orijinal jenere pa IA. Ranplase demo, konplete enfòmasyon antrepriz/politik, verifye dwa medya epi teste koneksyon sèvis yo anvan lansman piblik.

## Referans

- https://www.mux.com/docs/guides/upload-files-directly
- https://www.mux.com/docs/core/verify-webhook-signatures
- https://docs.cloud.google.com/translate/docs/basic/translating-text
- https://docs.cloud.google.com/translate/docs/reference/rpc/google.cloud.translate.v2
- https://firebase.google.com/docs/cloud-messaging/web/receive-messages
- https://firebase.google.com/docs/cloud-messaging/error-codes
- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/get_object.html
- https://support.google.com/adsense/answer/9727?hl=en

## Finalizasyon operasyon — V3

Gade `ETAP_MANYEL.md` pou lis presi etap ki mande kont/kle/enfòmasyon ou yo. `operations.py check` verifye konfigirasyon san montre sekrè yo. `operations.py backup` fè sovgad SQLite konsistan oswa PostgreSQL atravè pg_dump; `restore-sqlite` verifye backup la epi refize ekri sou yon baz ki deja egziste. Blueprint Render la pataje tout kle sèvis yo ant web ak worker epi dezaktive demo nan pwodiksyon. Sovgad hosting, monitoring, sèvis ekstèn, AdSense/CMP ak livrezon newsletter toujou mande aktivasyon oswa entegrasyon ki endike nan lis la.
