from typing import Optional
from app.persistence.abstract_persistence import PersistenceStrategy
from app.persistence.redis_persistence import RedisPersistence
from app.persistence.memory_persistence import InMemoryPersistence


class PersistenceFactory:
    """Factory for creating persistence strategy instances."""
    
    @staticmethod
    def create_persistence(
        strategy: str = "redis",
        redis_url: Optional[str] = None
    ) -> PersistenceStrategy:
        """
        Create a persistence strategy instance.
        
        Args:
            strategy: Type of persistence ("redis" or "memory")
            redis_url: Redis connection URL (only for redis strategy)
        
        Returns:
            PersistenceStrategy instance
        
        Raises:
            ValueError: If strategy is not supported
        """
        if strategy == "redis":
            return RedisPersistence(redis_url)
        elif strategy == "memory":
            return InMemoryPersistence()
        else:
            raise ValueError(f"Unsupported persistence strategy: {strategy}")