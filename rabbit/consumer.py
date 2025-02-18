import json
import asyncio

import pika
from tg_bot.main import bot

from repository import repository


repository = repository.Repository()


async def send_notification(user_chat_id, notification_message):
    await bot.send_message(user_chat_id, notification_message)


def callback(ch, method, properties, body):
    message = json.loads(body)
    team_name = message["team_name"]
    notification_message = message["message"]

    subscribed_users = repository.list_subscribed_users(team_name)

    for user in subscribed_users:
        asyncio.create_task(
            send_notification(
                user["id"], notification_message
            )
        )

    ch.basick_ack(delivery_tag=method.delivery_tag)


def consume_message(team_name):
    params = pika.ConnectionParameters(host="rabbit", port=5672)

    with pika.BlockingConnection(params) as connection:
        with connection.channel() as channel:
            channel.exchange_declare(exchange="matches", exchange_type="topic")

            queue = channel.queue_declare(queue="", exclusive=True)
            queue_name = queue.method.queue

            channel.queue_bind(
                exchange="matches",
                queue=queue_name,
                routing_key=f"matches.{team_name}"
                )

            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback
            )

            channel.start_consuming()
