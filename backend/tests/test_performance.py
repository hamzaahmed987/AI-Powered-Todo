"""
Unit tests for performance and caching utilities.

Tests caching mechanisms and performance optimizations.
"""

import time
import pytest
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

from app.utils.cache import SimpleCache, cached, invalidate_cache
from app.utils.performance import get_user_tasks_cached, invalidate_user_tasks_cache


class TestSimpleCache:
    """Test cases for SimpleCache class."""

    def test_cache_set_and_get(self):
        """Test basic set and get operations."""
        cache = SimpleCache()
        cache.set("test_key", "test_value", ttl=300)
        assert cache.get("test_key") == "test_value"

    def test_cache_expiration(self):
        """Test cache expiration."""
        cache = SimpleCache()
        cache.set("expiring_key", "expiring_value", ttl=0.1)  # Expire in 0.1 seconds
        assert cache.get("expiring_key") == "expiring_value"
        
        time.sleep(0.2)  # Wait for expiration
        assert cache.get("expiring_key") is None

    def test_cache_delete(self):
        """Test cache deletion."""
        cache = SimpleCache()
        cache.set("delete_key", "delete_value", ttl=300)
        assert cache.get("delete_key") == "delete_value"
        
        result = cache.delete("delete_key")
        assert result is True
        assert cache.get("delete_key") is None
        
        # Delete non-existent key
        result = cache.delete("nonexistent_key")
        assert result is False

    def test_cache_clear(self):
        """Test clearing entire cache."""
        cache = SimpleCache()
        cache.set("key1", "value1", ttl=300)
        cache.set("key2", "value2", ttl=300)
        
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cleanup_expired(self):
        """Test manual cleanup of expired entries."""
        cache = SimpleCache()
        cache.set("expired1", "value1", ttl=0.1)
        cache.set("expired2", "value2", ttl=0.1)
        cache.set("valid", "value3", ttl=300)
        
        time.sleep(0.2)  # Wait for expiration
        
        removed_count = cache.cleanup_expired()
        assert removed_count == 2
        assert cache.get("expired1") is None
        assert cache.get("expired2") is None
        assert cache.get("valid") == "value3"


class TestCachedDecorator:
    """Test cases for @cached decorator."""

    def test_cached_function(self):
        """Test that cached function returns cached value."""
        call_count = 0
        
        @cached(ttl=300)
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = test_func(5)
        assert result1 == 10
        assert call_count == 1
        
        result2 = test_func(5)  # Should come from cache
        assert result2 == 10
        assert call_count == 1  # Call count should not increase

    def test_cached_different_args(self):
        """Test that different arguments are cached separately."""
        call_count = 0
        
        @cached(ttl=300)
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = test_func(5)
        assert result1 == 10
        assert call_count == 1
        
        result2 = test_func(10)  # Different argument
        assert result2 == 20
        assert call_count == 2  # Should call function again
        
        result3 = test_func(5)  # Should come from cache
        assert result3 == 10
        assert call_count == 2  # Should not increase

    def test_cached_ttl_expiration(self):
        """Test that cached values expire after TTL."""
        call_count = 0
        
        @cached(ttl=0.1)  # Very short TTL
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = test_func(5)
        assert result1 == 10
        assert call_count == 1
        
        time.sleep(0.2)  # Wait for expiration
        
        result2 = test_func(5)  # Should call function again
        assert result2 == 10
        assert call_count == 2


class TestInvalidateCache:
    """Test cases for cache invalidation functions."""

    def test_invalidate_cache_pattern(self):
        """Test invalidating cache by pattern."""
        cache = SimpleCache()
        cache.set("prefix:1", "value1", ttl=300)
        cache.set("prefix:2", "value2", ttl=300)
        cache.set("other:1", "value3", ttl=300)
        
        assert cache.get("prefix:1") == "value1"
        assert cache.get("prefix:2") == "value2"
        assert cache.get("other:1") == "value3"
        
        invalidate_cache("prefix:")  # Invalidate all keys starting with "prefix:"
        
        assert cache.get("prefix:1") is None
        assert cache.get("prefix:2") is None
        assert cache.get("other:1") == "value3"  # Should remain

    def test_invalidate_cache_all(self):
        """Test invalidating entire cache."""
        cache = SimpleCache()
        cache.set("key1", "value1", ttl=300)
        cache.set("key2", "value2", ttl=300)
        
        invalidate_cache()  # Invalidate all
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None


class TestPerformanceUtils:
    """Test cases for performance utilities."""

    @patch('app.utils.performance.get_user_tasks_db')
    def test_get_user_tasks_cached(self, mock_get_user_tasks_db):
        """Test that get_user_tasks_cached uses caching."""
        from sqlalchemy.orm import Session
        from app.models.task import TaskStatus, TaskPriority
        
        # Mock the database function
        mock_task = Mock(spec=Task)
        mock_task.id = uuid4()
        mock_task.title = "Mock Task"
        mock_task.status = TaskStatus.PENDING
        mock_get_user_tasks_db.return_value = ([mock_task], 1)
        
        # Create a mock session
        mock_db = Mock(spec=Session)
        user_id = uuid4()
        
        # Call the function twice with same parameters
        result1 = get_user_tasks_cached(
            mock_db, user_id, TaskStatus.PENDING, TaskPriority.HIGH, 0, 20
        )
        result1_second_call = get_user_tasks_cached(
            mock_db, user_id, TaskStatus.PENDING, TaskPriority.HIGH, 0, 20
        )
        
        # The database function should only be called once due to caching
        assert mock_get_user_tasks_db.call_count == 1
        assert result1 == result1_second_call

    def test_invalidate_user_tasks_cache(self):
        """Test invalidating user task cache."""
        from app.utils.cache import cache
        
        # Add some entries to cache
        user_id = uuid4()
        cache.set(f"user_tasks:{user_id}:pending:high:0:20", "test_data", ttl=300)
        cache.set("other_cache_key", "other_data", ttl=300)
        
        assert cache.get(f"user_tasks:{user_id}:pending:high:0:20") == "test_data"
        assert cache.get("other_cache_key") == "other_data"
        
        # Invalidate user tasks cache
        invalidate_user_tasks_cache(user_id)
        
        assert cache.get(f"user_tasks:{user_id}:pending:high:0:20") is None
        assert cache.get("other_cache_key") == "other_data"  # Should remain