from typing import Dict, Any, List
from app.persistence.abstract_persistence import PersistenceStrategy


class InMemoryPersistence(PersistenceStrategy):
    """In-memory implementation of the PersistenceStrategy for testing."""
    
    def __init__(self):
        """Initialize in-memory storage."""
        self._storage: Dict[str, Dict[str, Any]] = {}
    
    def save(self, key: str, data: Dict[str, Any]) -> None:
        """Save data to in-memory dictionary."""
        self._storage[key] = data.copy()
    
    def load(self, key: str) -> Dict[str, Any]:
        """Load data from in-memory dictionary."""
        return self._storage.get(key, {}).copy()
    
    def delete(self, key: str) -> None:
        """Delete a key from in-memory dictionary."""
        if key in self._storage:
            del self._storage[key]
    
    def exists(self, key: str) -> bool:
        """Check if key exists in in-memory dictionary."""
        return key in self._storage
    
    def clear_all(self) -> None:
        """Clear all data from in-memory storage."""
        self._storage.clear()
    
    def list_tasks(self) -> List[str]:
        """
        List all saved TDD task keys.
        
        Returns:
            List of task keys (without 'state:' prefix)
        """
        keys = [k for k in self._storage.keys() if k.startswith("state:")]
        return [key.replace("state:", "") for key in keys]
    
    def get_all_data(self) -> Dict[str, Dict[str, Any]]:
        """Get all stored data (useful for debugging)."""
        return self._storage.copy()