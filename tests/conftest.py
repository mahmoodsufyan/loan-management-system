"""Run pytest against a disposable database, never an existing loans.db."""
import atexit
import os
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1] / '.test-data'
root.mkdir(exist_ok=True)
test_dir = tempfile.TemporaryDirectory(prefix='loans-', dir=root)
os.environ['DATABASE_URL'] = 'sqlite:///' + (Path(test_dir.name) / 'test.db').as_posix()

def cleanup():
    from app.db.session import engine
    engine.dispose()
    test_dir.cleanup()

atexit.register(cleanup)
