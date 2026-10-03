import hashlib,hmac,secrets,time,os
from fastapi import HTTPException
from db import one,write

def hash_password(password):
    salt=secrets.token_hex(16)
    digest=hashlib.scrypt(password.encode(),salt=salt.encode(),n=16384,r=8,p=1).hex()
    return 'scrypt$'+salt+'$'+digest

def verify_password(password,value):
    try:
        _,salt,digest=value.split('$')
        return hmac.compare_digest(hashlib.scrypt(password.encode(),salt=salt.encode(),n=16384,r=8,p=1).hex(),digest)
    except Exception: return False

def digest(v): return hashlib.sha256(v.encode()).hexdigest()
def session(request):
    token=request.cookies.get('vyora_staff','')
    if not token:return None
    return one('SELECT s.csrf,u.* FROM sessions s JOIN staff u ON s.staff_id=u.id WHERE s.token_hash=? AND s.expires>? AND u.active=1',(digest(token),int(time.time())))
def require(request,roles=None):
    u=session(request)
    if not u: raise HTTPException(401,'Konekte nan administrasyon an.')
    if roles and u['role'] not in roles: raise HTTPException(403,'Ou pa gen otorizasyon pou aksyon sa a.')
    return u

def csrf(request,token):
    u=require(request)
    if not hmac.compare_digest(u['csrf'],token or ''): raise HTTPException(403,'Sesyon ekspire. Rechaje paj la.')
    return u

def same_origin(request):
    origin=request.headers.get('origin')
    site=os.getenv('SITE_URL','').rstrip('/')
    if origin and origin.rstrip('/') not in [site,str(request.base_url).rstrip('/')]: raise HTTPException(403,'Origin invalid')

def rate(request,label,limit=15,seconds=600):
    ip=request.client.host if request.client else 'unknown'
    bucket=digest(ip+'|'+label+'|'+str(int(time.time())//seconds))
    now=int(time.time())
    write('INSERT INTO rate_limits(bucket,count,reset_at) VALUES (?,1,?) ON CONFLICT(bucket) DO UPDATE SET count=rate_limits.count+1',(bucket,now+seconds))
    r=one('SELECT count FROM rate_limits WHERE bucket=?',(bucket,))
    if r['count']>limit: raise HTTPException(429,'Twòp demann. Eseye ankò pita.')
    if secrets.randbelow(50)==0: write('DELETE FROM rate_limits WHERE reset_at<?',(now,))

def visitor(request): return digest(request.state.visitor)
