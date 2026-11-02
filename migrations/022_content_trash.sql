CREATE TABLE content_trash (
    content_type TEXT NOT NULL,
    content_id TEXT NOT NULL,
    previous_status TEXT NOT NULL,
    deleted_by TEXT NOT NULL,
    deleted_at TEXT NOT NULL,
    PRIMARY KEY(content_type,content_id)
);
