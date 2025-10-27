from typing import Dict, Any
from app.persistence.abstract_persistence import PersistenceStrategy


class InMemoryPersistence(PersistenceStrategy):
    """In-memory implementation of PersistenceStrategy for testing."""
    
    def __init__(self):
        self._storage: Dict[str, Dict[str, Any]] = {}
    
    def save(self, key: str, data: Dict[str, Any]) -> None:
        """Save data to in-memory storage."""
        # Deep copy to prevent external modifications
        import copy
        self._storage[key] = copy.deepcopy(data)
    
    def load(self, key: str) -> Dict[str, Any]:
        """Load data from in-memory storage."""
        import copy
        return copy.deepcopy(self._storage.get(key, {}))
    
    def delete(self, key: str) -> None:
        """Delete a key from in-memory storage."""
        self._storage.pop(key, None)
    
    def exists(self, key: str) -> bool:
        """Check if key exists in in-memory storage."""
        return key in self._storage
    
    def clear_all(self) -> None:
        """Clear all data from in-memory storage."""
        self._storage.clear()