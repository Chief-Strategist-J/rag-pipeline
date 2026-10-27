from typing import Optional, AsyncGenerator
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class ManagedConsumerGroup:
    def __init__(
        self,
        topic: str,
        group_id: str,
        bootstrap_servers: str = "localhost:9092"
    ) -> None:
        self._topic = topic
        self._group_id = group_id
        self._bootstrap_servers = bootstrap_servers
        self._consumer = None

    async def start(self) -> Result[bool, ApplicationError]:
        try:
            from aiokafka import AIOKafkaConsumer
            self._consumer = AIOKafkaConsumer(
                self._topic,
                bootstrap_servers=self._bootstrap_servers,
                group_id=self._group_id,
                enable_auto_commit=False,
                auto_offset_reset="earliest"
            )
            await self._consumer.start()
            return Ok(True)
        except Exception as err:
            return Err(ApplicationError(str(err), code="CONSUMER_START_FAILED", status_code=500))

    async def stop(self) -> Result[bool, ApplicationError]:
        try:
            if self._consumer is not None:
                await self._consumer.stop()
                self._consumer = None
            return Ok(True)
        except Exception as err:
            return Err(ApplicationError(str(err), code="CONSUMER_STOP_FAILED", status_code=500))

    async def fetch_one(self) -> Result[Optional[bytes], ApplicationError]:
        try:
            if self._consumer is None:
                return Err(ApplicationError("Consumer not running", code="CONSUMER_NOT_STARTED", status_code=500))
            msg = await self._consumer.getone()
            await self._consumer.commit()
            return Ok(msg.value)
        except Exception as err:
            return Err(ApplicationError(str(err), code="CONSUME_MESSAGE_FAILED", status_code=500))
