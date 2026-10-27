from typing import Any, Dict
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError
from messaging.engine.client.connection_pool import BrokerConnectionPool


class EventPublisher:
    def __init__(self, pool: BrokerConnectionPool) -> None:
        self._pool = pool

    async def publish(
        self,
        topic: str,
        key: str,
        payload_bytes: bytes
    ) -> Result[bool, ApplicationError]:
        try:
            producer = await self._pool.get_producer()
            if producer is not None:
                await producer.send_and_wait(
                    topic,
                    value=payload_bytes,
                    key=key.encode("utf-8")
                )
            return Ok(True)
        except Exception as err:
            return Err(ApplicationError(str(err), code="EVENT_PUBLISH_FAILED", status_code=500))
