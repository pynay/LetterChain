import redis
import hashlib
import logging
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.tracing import tracing_service
import json


logger = logging.getLogger(__name__)

class CacheService:
    """Redis-based caching service with automatic serialization"""

    def __init__(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        self._test_connection()

    def _test_connection(self):
        """Test Redis connection on startup"""
        try:
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            raise
    

    def _generate_key(self, prefix: str, content: str) -> str:
        """Generate cache key from content hash"""
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        return f"{prefix}:{content_hash}"
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from cache with automatic JSON deserialization"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except (json.JSONDecodeError, redis.RedisError) as e:
            logger.warning(f"Cache get failed for key {key}: {str(e)}")
            return None
        
    def set(
        self,
        key: str,
        value: Dict[str, Any],
        expire_seconds: int = 86400  # 24 hours default
    ) -> bool:
        """Set value in cache with automatic JSON serialization"""
        try:
            serialized = json.dumps(value)
            return self.redis_client.setex(key, expire_seconds, serialized)
        except (TypeError, redis.RedisError) as e:
            logger.warning(f"Cache set failed for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            return bool(self.redis_client.delete(key))
        except redis.RedisError as e:
            logger.warning(f"Cache delete failed for key {key}: {str(e)}")
            return False
    
    def get_parsed_resume(self, resume_text: str) -> Optional[Dict[str, Any]]:
        """Get cached parsed resume data"""
        key = self._generate_key("resume", resume_text)
        return self.get(key)
    
    def set_parsed_resume(
        self,
        resume_text: str,
        parsed_data: Dict[str, Any],
        expire_seconds: int = 86400
    ) -> bool:
        """Cache parsed resume data"""
        key = self._generate_key("resume", resume_text)
        return self.set(key, parsed_data, expire_seconds)
    
    def get_parsed_job(self, job_text: str) -> Optional[Dict[str, Any]]:
        """Get cached parsed job data"""
        key = self._generate_key("job", job_text)
        return self.get(key)
    
    def set_parsed_job(
        self,
        job_text: str,
        parsed_data: Dict[str, Any],
        expire_seconds: int = 86400
    ) -> bool:
        """Cache parsed job data"""
        key = self._generate_key("job", job_text)
        return self.set(key, parsed_data, expire_seconds)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        try:
            info = self.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }
        except redis.RedisError as e:
            logger.error(f"Failed to get cache stats: {str(e)}")
            return {"error": str(e)}

# Global cache service instance
cache_service = CacheService()
