CREATE TABLE submission_assets(id TEXT PRIMARY KEY,submission_id TEXT REFERENCES submissions(id),visitor_hash TEXT NOT NULL,object_key TEXT UNIQUE NOT NULL,content_type TEXT NOT NULL,size_bytes INTEGER NOT NULL,created_at TEXT NOT NULL);
CREATE INDEX submission_asset_parent ON submission_assets(submission_id);
