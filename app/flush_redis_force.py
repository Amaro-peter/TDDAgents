import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.persistence import PersistenceFactory

if __name__ == "__main__":
    print("🗑️  Flushing Redis...")
    persistence = PersistenceFactory.create_persistence("redis")
    persistence.clear_all()
    print("✅ Redis flushed successfully!")