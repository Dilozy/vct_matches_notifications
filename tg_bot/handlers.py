from aiogram.filters import Command, CommandStart
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery

from src.tg_bot.keyboards import (
    create_regions_kb, create_teams_in_region_kb,
    create_subscribed_teams
)
from src.repository import repository
from src.tg_bot.dependencies import container


handlers_router = Router()
repository = repository.Repository()


@handlers_router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer("Привет! Я бот, который будет оповещать тебя о матчах твоей любимой команды!\n" \
                        "Для того, чтобы подписаться на уведомления, введи команду /subscribe")


@handlers_router.message(Command("subscribe"))
async def subscribe_handler(message: Message) -> None:
    await message.answer(
        "Выбери регион, в котором играет твоя команда", reply_markup=create_regions_kb()
        )


@handlers_router.callback_query(F.data == "back_to_regions")
async def back_to_regions_handler(callback: CallbackQuery) -> None:
    await callback.message.delete()
    
    await callback.message.answer(
        "Выбери регион, в котором играет твоя команда", reply_markup=create_regions_kb()
        )


@handlers_router.callback_query(F.data.startswith("region:"))
async def team_choice_handler(callback: CallbackQuery) -> None:
    region = callback.data.split(":")[1]
    
    await callback.message.delete()

    await callback.message.answer(
        "Выбери команду, на которую хочешь подписаться",
        reply_markup=create_teams_in_region_kb(callback.message.chat.id, region)
    )


@handlers_router.callback_query(F.data.startswith("add:"))
async def confirm_team_choice_handler(callback: CallbackQuery) -> None:
    team = callback.data.split(":")[1]
    user_chat_id = callback.message.chat.id
    
    await callback.message.delete()

    if not repository.check_user(user_chat_id):
        repository.create_subscriber(user_chat_id)
    
    repository.add_subscription(user_chat_id, team)
    await container.user_consumer.bind_user(user_chat_id, team)
    
    await callback.message.answer(
        text=f"Оформлена подписка на команду <b>{team}</b>\n"
              "Ты будешь получать уведомления о матче за полчаса до начала, "
              "а также в момент старта матча",
              parse_mode="HTML")


@handlers_router.message(Command("unsubscribe"))
async def remove_subscription_handler(message: Message) -> None:
    await message.answer("Подписку на матчи какой команды вы хотели бы отменить?",
                         reply_markup=create_subscribed_teams(message.chat.id))
    


@handlers_router.callback_query(F.data.startswith("remove:"))
async def confirm_subscription_removal_handler(callback: CallbackQuery) -> None:
    removed_team = callback.data.split(":")[1]
    user_chat_id = callback.message.chat.id
    
    repository.remove_subscription(user_chat_id, removed_team)
    await container.user_consumer.unbind_user(user_chat_id, removed_team)

    await callback.message.delete()
    await callback.message.answer(f"Вы отменили подписку на матчи команды <b>{removed_team}</b>",
                                  parse_mode="HTML")
    

@handlers_router.message(Command("list_subscriptions"))
async def list_subscriptions_handler(message: Message) -> None:
    subscriptions_data = repository.list_user_subscriptions(message.chat.id)

    emea_teams = ', '.join(team for team in subscriptions_data
                           if subscriptions_data[team] == 'EMEA')
    americas_teams = ', '.join(team for team in subscriptions_data
                               if subscriptions_data[team] == 'Americas')
    pacific_teams = ', '.join(team for team in subscriptions_data
                              if subscriptions_data[team] == 'Pacific')
    china_teams = ', '.join(team for team in subscriptions_data
                            if subscriptions_data[team] == 'China')

    await message.answer(
        "Вот список команд, на которые вы подписаны:\n\n"
        f"<b>EMEA</b>: {emea_teams}\n"
        f"<b>Americas</b>: {americas_teams}\n"
        f"<b>Pacific</b>: {pacific_teams}\n"
        f"<b>China</b>: {china_teams}",
        parse_mode="HTML"
    )
