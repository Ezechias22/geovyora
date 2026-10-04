param([Parameter(Mandatory=$true)][string]$ProjectPath)
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $ProjectPath
if (!(Test-Path .\.env)) { throw "Fichye .env lokal la pa jwenn." }
if (!(Test-Path .\.venv\Scripts\python.exe)) { throw "Anviwonman Python pwoje a pa jwenn." }
$payload = @'
import json, sys
from dotenv import dotenv_values
config = dotenv_values('.env', interpolate=False)
keys = ['MUX_TOKEN_ID','MUX_TOKEN_SECRET','MUX_WEBHOOK_SECRET','S3_ENDPOINT_URL','S3_REGION','S3_BUCKET','S3_ACCESS_KEY_ID','S3_SECRET_ACCESS_KEY','MEDIA_PUBLIC_URL','PRIVATE_SUBMISSION_BUCKET','FIREBASE_PUBLIC_CONFIG','FIREBASE_SERVICE_ACCOUNT','FIREBASE_VAPID_KEY','GOOGLE_TRANSLATION_KEY']
defaults = {'S3_ENDPOINT_URL':'https://s3.us-west-004.backblazeb2.com','S3_REGION':'us-west-004','S3_BUCKET':'geovyora-images-public','MEDIA_PUBLIC_URL':'https://geovyora-images-public.s3.us-west-004.backblazeb2.com','PRIVATE_SUBMISSION_BUCKET':'geovyora-submissions-private'}
lines=[]
for key in keys:
    value=(config.get(key) or defaults.get(key) or '').strip()
    if not value: continue
    if key in ['FIREBASE_PUBLIC_CONFIG','FIREBASE_SERVICE_ACCOUNT']:
        try: value=json.dumps(json.loads(value),ensure_ascii=True,separators=(',',':'))
        except (ValueError,TypeError): raise SystemExit(key+' pa yon JSON valab. Verifye fichye .env la lokalman.')
    value=value.replace("'", "\\'")
    lines.append(key+"='"+value+"'")
if not any(line.startswith('MUX_TOKEN_ID=') or line.startswith('S3_ACCESS_KEY_ID=') for line in lines):
    raise SystemExit('Kle Mux/S3 yo pa jwenn nan .env sa a.')
lines += ['SITE_URL=https://geovyora-web.onrender.com','COOKIE_SECURE=1','SEED_DEMO=0','ALLOW_DEMO_CONTENT=0','AWS_REQUEST_CHECKSUM_CALCULATION=when_required']
# DATABASE_URL is intentionally excluded to preserve the deployed Neon database.
print('\n'.join(lines))
'@ | .\.venv\Scripts\python.exe -
if ($LASTEXITCODE -ne 0) { throw "Konfigirasyon an pa kopye. Gade mesaj ki anle a." }
Set-Clipboard -Value ($payload -join "`n")
Write-Host "Konfigirasyon sevis yo kopye pou Render. Pa kole yo nan chat ni nan GitHub." -ForegroundColor Green
Write-Host "Render > geovyora-web > Environment > Add from .env: kole, epi Save/Redeploy."
Write-Host "DATABASE_URL pa nan lis sa a: koneksyon Neon ki deja mache a pap ranplase."
