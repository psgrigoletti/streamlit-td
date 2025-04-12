"""Basic connection example.
"""
import redis

import sys
sys.path.append("..")

from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

class RedisManager:
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
            username="default",
            password=password,
        )

    def set_data(self, key, value):
        self.redis_client.set(key, value)

    def get_data(self, key):
        return self.redis_client.get(key)

    def delete_data(self, key):
        self.redis_client.delete(key)

    def exists(self, key):
        return self.redis_client.exists(key)
