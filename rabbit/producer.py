import json
import logging

import pika


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def produce_message(team1: str, team2: str, status: None | str = None) -> None:
    params = pika.ConnectionParameters(host="rabbit", port=5672)
    with pika.BlockingConnection(params) as connection:
        with connection.channel() as channel:
            message = {
                "team1": team1,
                "team2": team2,
                "message": f"Матч {team1} - {team2} начинается {status}"
            }
            
            logger.info("Publishing messages")

            channel.basic_publish(
                exchange="matches",
                routing_key=f"match.{team1}",
                body=json.dumps(message)
            )

            channel.basic_publish(
                exchange="matches",
                routing_key=f"match.{team2}",
                body=json.dumps(message)
            )



