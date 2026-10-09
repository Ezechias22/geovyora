ALTER TABLE influencers ADD COLUMN updated_at TEXT NOT NULL DEFAULT '';
UPDATE influencers SET updated_at=created_at WHERE updated_at='';
