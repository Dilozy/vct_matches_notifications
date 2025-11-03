import asyncio
import os

from aiogram import Bot

from src.db.repositories import TeamRepository
from src.domains import NotificationDTO


bot = Bot(token=os.getenv("BOT_TOKEN"))


class NotificationsService:
    MESSAGE_TEMPLATE = "Матч {} VS {} начинается {}"
    
    async def _send(self, notification_data: NotificationDTO):
        teams_subs = TeamRepository.list_subscribers([notification_data.team_1,
                                                      notification_data.team_2])
        
        message = self.MESSAGE_TEMPLATE.format(notification_data.team_1,
                                               notification_data.team_2,
                                               notification_data.status)        
        
        for sub in teams_subs:
            await bot.send_message(chat_id=sub.id, text=message)


def send_notifications(team1, team2, status):
    async def wrapper():
        notifications_svc = NotificationsService()
        notification_dto = NotificationDTO(team_1=team1, team_2=team2, status=status)
        await notifications_svc._send(notification_dto)

    asyncio.run(wrapper())
