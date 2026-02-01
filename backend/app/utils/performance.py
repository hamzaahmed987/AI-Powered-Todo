"""Performance optimization utilities.

Contains caching mechanisms and performance enhancements for the application.
"""

from typing import Optional, Tuple, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.task import Task, TaskStatus, TaskPriority
from app.services.task_service import get_user_tasks as get_user_tasks_db
from app.utils.cache import cached, invalidate_cache
import hashlib


def get_user_tasks_cached(
    db: Session,
    user_id: UUID,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[Task], int]:
    """
    Cached version of get_user_tasks with automatic cache invalidation.
    
    Args:
        db: Database session
        user_id: User UUID
        status: Filter by task status (optional)
        priority: Filter by task priority (optional)
        skip: Number of items to skip for pagination
        limit: Number of items to return
    
    Returns:
        Tuple of (tasks list, total count)
    """
    # Create a cache key based on all parameters
    cache_key = f"user_tasks:{user_id}:{status}:{priority}:{skip}:{limit}"
    
    # Try to get from cache first
    cached_result = _get_from_cache(cache_key)
    if cached_result:
        return cached_result
    
    # If not in cache, get from DB
    tasks, total = get_user_tasks_db(db, user_id, status, priority, skip, limit)
    
    # Store in cache
    _put_in_cache(cache_key, (tasks, total))
    
    return tasks, total


def _get_from_cache(key: str):
    """Internal function to get data from cache."""
    # This would use the actual cache implementation
    from app.utils.cache import cache
    return cache.get(key)


def _put_in_cache(key: str, value):
    """Internal function to put data in cache."""
    # This would use the actual cache implementation
    from app.utils.cache import cache
    cache.set(key, value, ttl=300)  # Cache for 5 minutes


def invalidate_user_tasks_cache(user_id: UUID):
    """Invalidate all cached task data for a specific user."""
    from app.utils.cache import invalidate_cache
    # This would invalidate all cache entries for this user
    # For now, we'll use a pattern that matches user task caches
    invalidate_cache(f"user_tasks:{user_id}:")


def invalidate_all_task_caches():
    """Invalidate all task-related caches."""
    from app.utils.cache import invalidate_cache
    invalidate_cache("user_tasks:")
    invalidate_cache("get_task:")