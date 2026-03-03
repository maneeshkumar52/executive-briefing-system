import asyncio
import json
import structlog
from typing import Any, Callable, Optional
from collections import defaultdict

logger = structlog.get_logger()
_local_queues: dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)


class ServiceBusHelper:
    def __init__(self, connection_string: str, local_mode: bool = True):
        self.local_mode = local_mode
        self.connection_string = connection_string

    async def publish(self, queue_name: str, message: dict) -> None:
        if self.local_mode:
            await _local_queues[queue_name].put(json.dumps(message))
            logger.info("service_bus.local.published", queue=queue_name)
            return
        # Real Service Bus implementation omitted for brevity (placeholder)
        logger.info("service_bus.published", queue=queue_name)

    async def subscribe(
        self,
        queue_name: str,
        handler: Callable,
        max_wait: int = 60,
    ) -> Any:
        if self.local_mode:
            try:
                msg_str = await asyncio.wait_for(
                    _local_queues[queue_name].get(), timeout=max_wait
                )
                return await handler(json.loads(msg_str))
            except asyncio.TimeoutError:
                logger.warning("service_bus.local.timeout", queue=queue_name)
                return None
        logger.info("service_bus.subscribe", queue=queue_name)
        return None
