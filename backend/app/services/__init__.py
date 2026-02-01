"""Services package.

Exports all service functions for business logic.
"""

from .auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    create_tokens,
)
from .user_service import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user,
    deactivate_user,
)
from .task_service import (
    create_task,
    get_task,
    get_user_tasks,
    update_task,
    delete_task,
    can_access_task,
    update_ai_suggestions,
)
from .ai_service import (
    generate_priority_and_duration,
    analyze_task_query,
    suggest_subtasks,
)

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "create_tokens",
    "create_user",
    "get_user_by_email",
    "get_user_by_id",
    "update_user",
    "deactivate_user",
    "create_task",
    "get_task",
    "get_user_tasks",
    "update_task",
    "delete_task",
    "can_access_task",
    "update_ai_suggestions",
    "generate_priority_and_duration",
    "analyze_task_query",
    "suggest_subtasks",
]
