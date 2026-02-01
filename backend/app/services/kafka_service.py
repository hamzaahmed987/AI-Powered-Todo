"""Kafka event streaming service for Phase V.

Handles publishing and consuming task events via Kafka.
"""

import json
import os
from typing import Optional, Any
from datetime import datetime
from enum import Enum
from uuid import UUID

from app.utils.logger import get_logger

logger = get_logger(__name__)


class EventType(str, Enum):
    """Types of events published to Kafka."""
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_DELETED = "task.deleted"
    TASK_COMPLETED = "task.completed"
    REMINDER_DUE = "reminder.due"
    RECURRING_TASK_GENERATED = "recurring.generated"
    AI_REQUEST = "ai.request"
    AI_RESPONSE = "ai.response"


class KafkaService:
    """Service for Kafka event streaming.

    Publishes task events to Kafka topics for distributed processing.
    Falls back gracefully when Kafka is not available.
    """

    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.enabled = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
        self.producer = None
        self._initialize_producer()

    def _initialize_producer(self):
        """Initialize Kafka producer if available."""
        if not self.enabled:
            logger.info("Kafka disabled, events will be logged only")
            return

        try:
            from aiokafka import AIOKafkaProducer
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
            )
            logger.info(f"Kafka producer initialized: {self.bootstrap_servers}")
        except ImportError:
            logger.warning("aiokafka not installed, Kafka events disabled")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            self.enabled = False

    async def start(self):
        """Start the Kafka producer."""
        if self.producer:
            await self.producer.start()

    async def stop(self):
        """Stop the Kafka producer."""
        if self.producer:
            await self.producer.stop()

    async def publish_event(
        self,
        event_type: EventType,
        topic: str,
        data: dict[str, Any],
        key: Optional[str] = None
    ) -> bool:
        """Publish an event to Kafka.

        Args:
            event_type: Type of event
            topic: Kafka topic to publish to
            data: Event payload
            key: Optional partition key

        Returns:
            bool: True if published successfully
        """
        event = {
            "event_type": event_type.value,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }

        # Always log the event
        logger.info(f"Event: {event_type.value} on {topic}", extra={"event": event})

        if not self.enabled or not self.producer:
            return True  # Graceful degradation

        try:
            await self.producer.send_and_wait(
                topic,
                value=event,
                key=key.encode() if key else None
            )
            return True
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False

    async def publish_task_created(self, task_id: UUID, user_id: UUID, title: str):
        """Publish task created event."""
        await self.publish_event(
            EventType.TASK_CREATED,
            "task-events",
            {"task_id": str(task_id), "user_id": str(user_id), "title": title},
            key=str(user_id)
        )

    async def publish_task_updated(self, task_id: UUID, user_id: UUID, changes: dict):
        """Publish task updated event."""
        await self.publish_event(
            EventType.TASK_UPDATED,
            "task-events",
            {"task_id": str(task_id), "user_id": str(user_id), "changes": changes},
            key=str(user_id)
        )

    async def publish_task_deleted(self, task_id: UUID, user_id: UUID):
        """Publish task deleted event."""
        await self.publish_event(
            EventType.TASK_DELETED,
            "task-events",
            {"task_id": str(task_id), "user_id": str(user_id)},
            key=str(user_id)
        )

    async def publish_task_completed(self, task_id: UUID, user_id: UUID, title: str):
        """Publish task completed event."""
        await self.publish_event(
            EventType.TASK_COMPLETED,
            "task-events",
            {"task_id": str(task_id), "user_id": str(user_id), "title": title},
            key=str(user_id)
        )

    async def publish_reminder(self, task_id: UUID, user_id: UUID, title: str, deadline: datetime):
        """Publish reminder due event."""
        await self.publish_event(
            EventType.REMINDER_DUE,
            "notifications",
            {
                "task_id": str(task_id),
                "user_id": str(user_id),
                "title": title,
                "deadline": deadline.isoformat() if deadline else None
            },
            key=str(user_id)
        )

    async def publish_ai_request(self, user_id: UUID, query: str, context: dict):
        """Publish AI request event for processing."""
        await self.publish_event(
            EventType.AI_REQUEST,
            "ai-requests",
            {"user_id": str(user_id), "query": query, "context": context},
            key=str(user_id)
        )


# Singleton instance
kafka_service = KafkaService()
