import aio_pika
import json
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from aio_pika import Channel

from aiogram import Bot


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserConsumer:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @asynccontextmanager
    async def _get_channel(self) -> AsyncGenerator[Channel, None]:
        """Автоматически создает и закрывает соединение и канал"""
        connection = await aio_pika.connect_robust("amqp://guest:guest@rabbit:5672/")
        try:
            channel = await connection.channel()
            yield channel
        finally:
            await connection.close()

    async def send_notification(self, user_chat_id: int, message: str) -> None:
        try:
            await self.bot.send_message(user_chat_id, message)
            logger.info(f"Notification sent to {user_chat_id}")
        except Exception as e:
            logger.error(f"Failed to send to {user_chat_id}: {e}")

    async def _process_message(self, user_id: int, message: aio_pika.IncomingMessage) -> None:
        async with message.process():
            try:
                body = json.loads(message.body.decode())
                if msg := body.get("message"):
                    await self.send_notification(user_id, msg)
                else:
                    logger.error(f"Invalid message: {body}")
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                logger.error(f"Decode error: {e}")
            except Exception as e:
                logger.error(f"Processing error: {e}")

    async def bind_user(self, user_id: int, team_name: str) -> None:
        try:         
            logger.info(f"User {user_id} subscribed to team {team_name}")

            asyncio.create_task(self._listen_queue(user_id, team_name))
                
        except Exception as e:
            logger.error(f"Subscribe error for {user_id}/{team_name}: {e}")

    async def _listen_queue(self, user_id: int, team_name: str) -> None:
        try:
            async with self._get_channel() as channel:
                queue = await channel.get_queue(f"team.{team_name}.notifications")
                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        logger.info(f"Received message for user {user_id}: {message.body.decode()}")
                        await self._process_message(user_id, message)
        except Exception as e:
            logger.error(f"Listen error for {user_id}/{team_name}: {e}")

    async def unbind_user(self, user_id: int, team_name: str) -> None:
        try:
            async with self._get_channel() as channel:
                queue = await channel.get_queue(
                    f"user_{user_id}_queue",
                    ensure=False
                )
                
                if not queue:
                    logger.warning(f"Queue for {user_id} not found")
                    return
                
                await queue.unbind(
                    exchange="matches",
                    routing_key=f"matches.team.{team_name}"
                )
                logger.info(f"Unbound {user_id} from {team_name}")
                    
        except Exception as e:
            logger.error(f"Unbind error for {user_id}/{team_name}: {e}")
