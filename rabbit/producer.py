import json

import pika


def produce_message(team_name, opponent, status=None):
    params = pika.ConnectionParameters(host="rabbit", port=5672)

    with pika.BlockingConnection(params) as connection:
        with connection.channel() as channel:

            channel.exchange_declare(exchange="matches", exchange_type="topic")

            message = {
                "team_name": team_name,
                "message": f"Матч {team_name} против {opponent} начинается {status}"
            }

            channel.basic_publish(
                exchange="matches",
                routing_key=f"matches.{team_name}",
                body=json.dumps(message)
            )
