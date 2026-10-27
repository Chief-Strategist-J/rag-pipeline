from typing import Optional
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class BrokerConnectionPool:
    def __init__(self, bootstrap_servers: str = "localhost:9092") -> None:
        self._bootstrap_servers = bootstrap_servers
        self._producer = None

    async def get_producer(self):
        if self._producer is None:
            try:
                from aiokafka import AIOKafkaProducer
                self._producer = AIOKafkaProducer(
                    bootstrap_servers=self._bootstrap_servers,
                    request_timeout_ms=5000
                )
                await self._producer.start()
            except Exception:
                self._producer = None
        return self._producer

    async def close(self) -> None:
        if self._producer is not None:
            try:
                await self._producer.stop()
            except Exception:
                pass
            finally:
                self._producer = None
