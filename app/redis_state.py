import redis
import json
from app.config import Config

class RedisState:
    def __init__(self):
        self.client = redis.from_url(Config.REDIS_URL)

    def save(self, key: str, data: dict):
        self.client.set(key, json.dumps(data, indent=2))

    def load(self, key: str):
        raw = self.client.get(key)
        if raw:
            return json.loads(raw)
        return {}

    def clear(self, key: str):
        self.client.delete(key)

        
