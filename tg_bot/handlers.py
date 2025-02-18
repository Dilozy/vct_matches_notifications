from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from .keyboards import (
    create_regions_kb, create_teams_in_region_kb,
    create_subscribed_teams, request_location_kb
)
from .misc import get_timezone_by_coordinates
from repository import repository


router = Router()
repository = repository.Repository()


@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! Я бот, который будет оповещать тебя о матчах твоей любимой команды!\n" \
                        "Для того, чтобы подписаться на уведомления, введи команду /subscribe")


@router.message(Command("subscribe"))
async def subscribe_handler(message: Message):
    await message.answer(
        "Выбери регион, в котором играет твоя команда", reply_markup=create_regions_kb()
        )


@router.callback_query(F.data == "back_to_regions")
async def back_to_regions_handler(callback: CallbackQuery):
    await callback.message.delete()
    
    await callback.message.answer(
        "Выбери регион, в котором играет твоя команда", reply_markup=create_regions_kb()
        )


@router.callback_query(F.data.startswith("region:"))
async def team_choice_handler(callback: CallbackQuery):
    region = callback.data.split(":")[1]
    
    await callback.message.delete()

    await callback.message.answer(
        "Выбери команду, на которую хочешь подписаться",
        reply_markup=create_teams_in_region_kb(callback.message.chat.id, region)
    )


@router.callback_query(F.data.startswith("add:"))
async def confirm_team_choice_handler(callback: CallbackQuery):
    team = callback.data.split(":")[1]
    
    await callback.message.delete()

    if repository.check_user(callback.message.chat.id):
        repository.add_subscription(callback.message.chat.id, team)
        
        await callback.message.answer(
        text=f"Оформлена подписка на команду <b>{team}</b>\n" \
              "Ты будешь получать уведомления о матчах за час до, " \
              "а также в момент начала матча",
        parse_mode="HTML")
    
    else:
        await ask_user_location(callback.message)



@router.message(Command("unsubscribe"))
async def remove_subscription_handler(message: Message):
    await message.answer("Подписку на матчи какой команды вы хотели бы отменить?",
                         reply_markup=create_subscribed_teams(message.chat.id))


@router.callback_query(F.data.startswith("remove:"))
async def confirm_subscription_removal_handler(callback: CallbackQuery):
    removed_team = callback.data.split(":")[1]
    
    repository.remove_subscription(callback.message.chat.id, removed_team)

    await callback.message.delete()
    await callback.message.answer(f"Вы отменили подписку на матчи команды <b>{removed_team}</b>",
                                  parse_mode="HTML")
    

@router.message(Command("list_subscriptions"))
async def list_subscriptions_handler(message: Message):
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


async def ask_user_location(message: Message):
    await message.answer(
        "Чтобы уведомления о матчах приходили в корректное время "
        "небходима информация о вашем часовом поясе. Для уточнения часового пояса "
        "отправьте, пожалуйста, вашу геопозицию. Бот сохранит только данные "
        "о вашем часовом поясе", reply_markup=request_location_kb()
        )


@router.message(F.location)
async def get_user_timezone(message: Message):
    await handle_location_message(message)


async def handle_location_message(message: Message):
    """
    Обрабатывает сообщение с геолокацией и отправляет пользователю его временной пояс.
    """
    lat, lon = message.location.latitude, message.location.longitude
    timezone = get_timezone_by_coordinates(lat, lon)

    if timezone:
        repository.create_subscriber(message.chat.id, timezone)
        
        await message.answer(
            f"Ваш часовой пояс <b>({timezone})</b> успешно сохранен.\n\n"
            "Теперь вы можете подписаться на уведомления о матчах "
            "командой /subscribe",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML"
            )
        
    else:
        await message.answer(
            "Не удалось определить часовой пояс для вашего местоположения.",
            reply_markup=ReplyKeyboardRemove()
            )

    await message.delete()