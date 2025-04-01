from aiogram import Bot
from rabbit.user_consumer import UserConsumer


class DIContainer:
    def __init__(self) -> None:
        self.bot: Bot | None = None
        self.user_consumer: UserConsumer | None = None

    def initialize(self, bot: Bot) -> None:
        self.bot = bot
        self.user_consumer = UserConsumer(bot)

container = DIContainer()