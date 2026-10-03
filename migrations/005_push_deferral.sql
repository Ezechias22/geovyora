ALTER TABLE deliveries ADD COLUMN next_try TEXT NOT NULL DEFAULT '';
CREATE INDEX delivery_queue_retry ON deliveries(status,next_try);
