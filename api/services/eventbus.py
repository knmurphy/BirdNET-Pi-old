"""EventBus for real-time detection events using asyncio pub/sub."""

import asyncio
import json
from dataclasses import dataclass, asdict
from typing import AsyncGenerator


@dataclass
class DetectionEvent:
    """Event fired when a new detection is made."""

    id: int
    com_name: str
    sci_name: str
    confidence: float
    date: str
    time: str
    iso8601: str
    file_name: str
    classifier: str

    def to_sse_data(self) -> str:
        """Convert to SSE data format (JSON-encoded)."""
        return json.dumps(asdict(self))


class EventBus:
    """Async pub/sub event bus for detection events.

    Allows multiple SSE subscribers to receive real-time detection events.
    Uses asyncio.Queue for each subscriber to handle backpressure.
    """

    def __init__(self):
        self._subscribers: list[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        """Subscribe to detection events.

        Returns:
            Queue that will receive DetectionEvent objects.
        """
        queue: asyncio.Queue[DetectionEvent | None] = asyncio.Queue()
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        """Unsubscribe from detection events.

        Args:
            queue: The queue returned by subscribe().
        """
        try:
            self._subscribers.remove(queue)
        except ValueError:
            pass

    async def publish(self, event: DetectionEvent) -> int:
        """Publish a detection event to all subscribers.

        Args:
            event: The detection event to publish.

        Returns:
            Number of subscribers that received the event.
        """
        delivered = 0
        for queue in list(self._subscribers):  # snapshot copy
            try:
                queue.put_nowait(event)
                delivered += 1
            except asyncio.QueueFull:
                # Queue is full, skip this subscriber
                pass
        return delivered

    async def event_stream(self, queue: asyncio.Queue) -> AsyncGenerator[str, None]:
        """Generate SSE event stream from queue.

        Args:
            queue: Queue from subscribe().

        Yields:
            SSE-formatted strings.
        """
        try:
            while True:
                event = await queue.get()
                if event is None:
                    # Shutdown signal
                    break
                yield f"data: {event.to_sse_data()}\n\n"
        finally:
            self.unsubscribe(queue)

    @property
    def subscriber_count(self) -> int:
        """Number of active subscribers."""
        return len(self._subscribers)


# Global event bus instance
event_bus = EventBus()
