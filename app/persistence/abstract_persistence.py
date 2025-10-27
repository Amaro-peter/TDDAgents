from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class PersistenceStrategy(ABC):
    """Abstract base class for persistence strategies following DIP."""
    
    @abstractmethod
    def save(self, key: str, data: Dict[str, Any]) -> None:
        """Save data to the persistence layer."""
        pass
    
    @abstractmethod
    def load(self, key: str) -> Dict[str, Any]:
        """Load data from the persistence layer."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete data from the persistence layer."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in the persistence layer."""
        pass
    
    @abstractmethod
    def clear_all(self) -> None:
        """Clear all data from the persistence layer."""
        pass


class VectorPersistenceStrategy(ABC):
    """Abstract base class for vector database operations."""
    
    @abstractmethod
    def store_embedding(self, key: str, vector: List[float], metadata: Dict[str, Any]) -> None:
        """Store a vector embedding with metadata."""
        pass
    
    @abstractmethod
    def search_similar(self, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        pass
    
    @abstractmethod
    def delete_embedding(self, key: str) -> None:
        """Delete a vector embedding."""
        pass