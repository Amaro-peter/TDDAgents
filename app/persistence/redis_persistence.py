import redis
import json
from typing import Dict, Any, Optional
from app.persistence.abstract_persistence import PersistenceStrategy
from app.config import Config


class RedisPersistence(PersistenceStrategy):
    """Redis implementation of the PersistenceStrategy."""
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize Redis client.
        
        Args:
            redis_url: Redis connection URL. If None, uses Config.REDIS_URL
        """
        url = redis_url or Config.REDIS_URL
        self.client = redis.from_url(url, decode_responses=True)
    
    def save(self, key: str, data: Dict[str, Any]) -> None:
        """Save data to Redis as JSON."""
        try:
            serialized = json.dumps(data, indent=2)
            self.client.set(key, serialized)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Failed to serialize data for key '{key}': {str(e)}")
        except redis.RedisError as e:
            raise ConnectionError(f"Failed to save to Redis: {str(e)}")
    
    def load(self, key: str) -> Dict[str, Any]:
        """Load data from Redis."""
        try:
            raw = self.client.get(key)
            if raw:
                return json.loads(raw)
            return {}
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to deserialize data for key '{key}': {str(e)}")
        except redis.RedisError as e:
            raise ConnectionError(f"Failed to load from Redis: {str(e)}")
    
    def delete(self, key: str) -> None:
        """Delete a key from Redis."""
        try:
            self.client.delete(key)
        except redis.RedisError as e:
            raise ConnectionError(f"Failed to delete from Redis: {str(e)}")
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            return bool(self.client.exists(key))
        except redis.RedisError as e:
            raise ConnectionError(f"Failed to check existence in Redis: {str(e)}")
    
    def clear_all(self) -> None:
        """Clear all keys from the current Redis database."""
        try:
            self.client.flushdb()
        except redis.RedisError as e:
            raise ConnectionError(f"Failed to clear Redis: {str(e)}")
    
    def get_client(self) -> redis.Redis:
        """Get the underlying Redis client for advanced operations."""
        return self.client