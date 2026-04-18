import redis
import json
import pickle
from utils.config import Config
from utils.logging import log_info, log_error
import time
import os

class RedisCache:
    def __init__(self):
        # Check if Redis is explicitly disabled
        redis_disabled = os.getenv('DISABLE_REDIS', '').lower() in ('true', '1', 'yes')
        
        if redis_disabled:
            log_info("Redis explicitly disabled, using in-memory cache")
            self.use_redis = False
            self._init_memory_cache()
            return
            
        try:
            self.redis_client = redis.from_url(Config.REDIS_URL)
            # Test connection
            self.redis_client.ping()
            log_info("Redis cache connected successfully")
            self.use_redis = True
        except Exception as e:
            log_error(f"Failed to connect to Redis: {str(e)}")
            log_info("Falling back to in-memory cache")
            self.use_redis = False
            self._init_memory_cache()
    
    def _init_memory_cache(self):
        """Initialize in-memory cache"""
        self.memory_cache = {}
        self.cache_expiry = {}
    
    def set(self, key, value, ttl=86400):  # Default TTL: 24 hours
        """Set a key-value pair in cache with TTL"""
        if self.use_redis:
            try:
                # Serialize the value
                if isinstance(value, dict) or isinstance(value, list):
                    serialized_value = json.dumps(value)
                else:
                    serialized_value = str(value)
                    
                result = self.redis_client.setex(key, ttl, serialized_value)
                log_info(f"Cache SET: {key}")
                return result
            except Exception as e:
                log_error(f"Failed to set cache key {key}: {str(e)}")
                # Fall back to memory cache if Redis fails
                self.use_redis = False
                self._init_memory_cache()
                return self.set(key, value, ttl)  # Retry with memory cache
        else:
            # In-memory cache fallback
            try:
                self.memory_cache[key] = value
                self.cache_expiry[key] = time.time() + ttl
                log_info(f"Memory Cache SET: {key}")
                return True
            except Exception as e:
                log_error(f"Failed to set memory cache key {key}: {str(e)}")
                return False
    
    def get(self, key):
        """Get a value from cache by key"""
        if self.use_redis:
            try:
                value = self.redis_client.get(key)
                if value is None:
                    log_info(f"Cache MISS: {key}")
                    return None
                    
                log_info(f"Cache HIT: {key}")
                # Try to deserialize as JSON, fallback to string
                try:
                    return json.loads(value)
                except:
                    return value.decode('utf-8') if isinstance(value, bytes) else value
            except Exception as e:
                log_error(f"Failed to get cache key {key}: {str(e)}")
                # Fall back to memory cache if Redis fails
                self.use_redis = False
                self._init_memory_cache()
                return self.get(key)  # Retry with memory cache
        else:
            # In-memory cache fallback
            try:
                if key in self.memory_cache:
                    # Check if expired
                    if time.time() > self.cache_expiry.get(key, 0):
                        del self.memory_cache[key]
                        if key in self.cache_expiry:
                            del self.cache_expiry[key]
                        log_info(f"Memory Cache EXPIRED: {key}")
                        return None
                    log_info(f"Memory Cache HIT: {key}")
                    return self.memory_cache[key]
                log_info(f"Memory Cache MISS: {key}")
                return None
            except Exception as e:
                log_error(f"Failed to get memory cache key {key}: {str(e)}")
                return None
    
    def delete(self, key):
        """Delete a key from cache"""
        if self.use_redis:
            try:
                result = self.redis_client.delete(key)
                log_info(f"Cache DELETE: {key}")
                return result > 0
            except Exception as e:
                log_error(f"Failed to delete cache key {key}: {str(e)}")
                # Fall back to memory cache if Redis fails
                self.use_redis = False
                self._init_memory_cache()
                return self.delete(key)  # Retry with memory cache
        else:
            # In-memory cache fallback
            try:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                    if key in self.cache_expiry:
                        del self.cache_expiry[key]
                    log_info(f"Memory Cache DELETE: {key}")
                    return True
                return False
            except Exception as e:
                log_error(f"Failed to delete memory cache key {key}: {str(e)}")
                return False
    
    def flush(self):
        """Clear all cache entries"""
        if self.use_redis:
            try:
                self.redis_client.flushdb()
                log_info("Cache flushed")
                return True
            except Exception as e:
                log_error(f"Failed to flush cache: {str(e)}")
                # Fall back to memory cache if Redis fails
                self.use_redis = False
                self._init_memory_cache()
                return self.flush()  # Retry with memory cache
        else:
            # In-memory cache fallback
            try:
                self.memory_cache.clear()
                self.cache_expiry.clear()
                log_info("Memory Cache flushed")
                return True
            except Exception as e:
                log_error(f"Failed to flush memory cache: {str(e)}")
                return False

# Global cache instance
cache = RedisCache()