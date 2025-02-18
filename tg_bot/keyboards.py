from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from repository import repository

repository = repository.Repository()


def create_regions_kb() -> InlineKeyboardMarkup:
    regions = ("EMEA", "Americas", "China", "Pacific")
    kb = InlineKeyboardBuilder()

    buttons = (InlineKeyboardButton(text=region, callback_data=f"region:{region}") for region in regions)

    for button in buttons:
        kb.row(button)

    return kb.as_markup()


def create_teams_in_region_kb(user_chat_id: int, region: str) -> InlineKeyboardMarkup:
    teams = repository.select_not_subscribed_teams(user_chat_id, region)

    kb = InlineKeyboardBuilder()

    buttons = (InlineKeyboardButton(text=team, callback_data=f"add:{team}") for team in teams)

    for button in buttons:
        kb.row(button)
    
    kb.row(InlineKeyboardButton(text="Назад", callback_data="back_to_regions"))

    return kb.as_markup()


def create_subscribed_teams(user_chat_id: int) -> InlineKeyboardMarkup:
    teams = repository.list_user_subscriptions(user_chat_id)

    kb = InlineKeyboardBuilder()

    buttons = (InlineKeyboardButton(text=team, callback_data=f"remove:{team}") for team in teams)

    for button in buttons:
        kb.row(button)

    return kb.as_markup()


def request_location_kb():
    button = KeyboardButton(text="Отправить геолокацию", request_location=True)
    kb = ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True)
    
    return kb