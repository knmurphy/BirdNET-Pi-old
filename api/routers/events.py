"""Server-Sent Events endpoint for real-time detection stream."""

import asyncio
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.services.eventbus import event_bus

router = APIRouter()


@router.get("/events")
async def event_stream():
    """Server-Sent Events stream for real-time detection events.

    Clients can connect to receive detection events as they happen.
    Heartbeat comments are sent every 15 seconds to keep connections alive.
    """
    
    async def generate():
        """Generate SSE event stream."""
        # Send initial connection message
        yield f"event: connected\ndata: {{\"timestamp\": \"{datetime.now().isoformat()}\"}}\n\n"
        
        # Subscribe to detection events
        queue = event_bus.subscribe()
        
        try:
            # Wait for events
            while True:
                try:
                    # Check for event with timeout (slightly longer than heartbeat interval)
                    event = await asyncio.wait_for(queue.get(), timeout=20.0)
                    if event is None:
                        break
                    yield f"event: detection\ndata: {event.to_sse_data()}\n\n"
                except asyncio.TimeoutError:
                    # Send heartbeat on timeout (every ~15-20 seconds)
                    yield ": heartbeat\n\n"
                    
        except asyncio.CancelledError:
            # Client disconnected
            pass
        finally:
            event_bus.unsubscribe(queue)
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
