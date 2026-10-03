"""Secure console-only staff setup and maintenance. Never ships a default password."""
import argparse,getpass,uuid,sys
from db import migrate,one,write
from security import hash_password
p=argparse.ArgumentParser();p.add_argument('command',choices=['create-admin','reset-password','disable-staff','migrate']);p.add_argument('--email');p.add_argument('--name');a=p.parse_args();migrate()
if a.command=='migrate':print('Migrations applied.');sys.exit()
email=(a.email or input('Staff email: ')).strip().lower()
if '@' not in email:raise SystemExit('Valid email required.')
user=one('SELECT * FROM staff WHERE email=?',(email,))
if a.command=='disable-staff':
 if not user:raise SystemExit('Staff not found.')
 if user['role']=='super_admin' and one("SELECT count(*) n FROM staff WHERE role='super_admin' AND active=1")['n']<=1:raise SystemExit('Cannot disable the final super admin.')
 write('UPDATE staff SET active=0 WHERE id=?',(user['id'],));write('DELETE FROM sessions WHERE staff_id=?',(user['id'],));print('Staff disabled, sessions revoked.');sys.exit()
if a.command=='create-admin' and user:raise SystemExit('Staff already exists; use reset-password.')
if a.command=='reset-password' and not user:raise SystemExit('Staff not found.')
password=getpass.getpass('Password (minimum 12 characters): ')
if len(password)<12:raise SystemExit('Minimum 12 characters.')
if password!=getpass.getpass('Confirm password: '):raise SystemExit('Passwords differ.')
if user:write('UPDATE staff SET password_hash=? WHERE id=?',(hash_password(password),user['id']));write('DELETE FROM sessions WHERE staff_id=?',(user['id'],))
else:
 name=(a.name or input('Display name: ')).strip()
 if not name:raise SystemExit('Name required.')
 write('INSERT INTO staff(id,email,name,password_hash,role) VALUES (?,?,?,?,?)',(str(uuid.uuid4()),email,name,hash_password(password),'super_admin'))
print('Staff saved. Password was not stored in plaintext.')
