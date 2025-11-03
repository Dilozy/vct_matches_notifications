import os
import asyncio

import aiohttp

from src.db.repositories import TeamRepository
from src.domains import NotificationDTO


_loop = asyncio.new_event_loop()


class NotificationsClient:
    async def send_notifications_coro(self, notif_data: NotificationDTO):
        sub_ids = TeamRepository.list_subscribers([notif_data.team_1,
                                                   notif_data.team_2])
        
        message = await self._build_notification_messsage(notif_data)
        
        await self._send(sub_ids=sub_ids, message=message)

    async def _build_notification_messsage(self, notif_data):
        return f"Матч {notif_data.team_1} VS {notif_data.team_2} начинается {notif_data.status}"
    
    async def _send(self, sub_ids, message):
        url = f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage"
        
        async with aiohttp.ClientSession() as session:
            for sub_id in sub_ids:
                payload = {"chat_id": sub_id, "text": message}
                await session.post(url=url, json=payload, timeout=10)


notifications_client = NotificationsClient()


def send_notifications(team1, team2, status):
    async def wrapper():
        notification_dto = NotificationDTO(team_1=team1, team_2=team2, status=status)
        await notifications_client.send_notifications_coro(notification_dto)

    _loop.run_until_complete(wrapper())
