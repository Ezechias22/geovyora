import tempfile,unittest,sqlite3
from pathlib import Path
from unittest.mock import patch
import test_workflows  # Initialize isolated test database before importing db.
import operations
class Backups(unittest.TestCase):
    def test_backup_restore_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'source.sqlite3';saved=root/'backup.sqlite3';restored=root/'restored.sqlite3'
            with sqlite3.connect(source) as c:
                c.execute('CREATE TABLE sample(value TEXT)');c.execute("INSERT INTO sample VALUES ('Geovyora')")
            with patch.object(operations.db,'URL',''),patch.object(operations.db,'PATH',str(source)):
                operations.backup(saved)
                with self.assertRaises(ValueError):operations.backup(saved)
            operations.restore_sqlite(saved,restored)
            with sqlite3.connect(restored) as c:self.assertEqual(c.execute('SELECT value FROM sample').fetchone()[0],'Geovyora')
            with self.assertRaises(ValueError):operations.restore_sqlite(saved,restored)
    def test_invalid_backup_does_not_create_destination(self):
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'invalid';source.write_text('not a database');target=Path(folder)/'new'
            with self.assertRaises(sqlite3.DatabaseError):operations.restore_sqlite(source,target)
            self.assertFalse(target.exists())
