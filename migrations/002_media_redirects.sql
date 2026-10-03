CREATE TABLE media_assets(id TEXT PRIMARY KEY,object_key TEXT UNIQUE NOT NULL,url TEXT NOT NULL,content_type TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'pending',staff_id TEXT NOT NULL REFERENCES staff(id),created_at TEXT NOT NULL);
CREATE TABLE redirects(old_slug TEXT PRIMARY KEY,new_slug TEXT NOT NULL);
