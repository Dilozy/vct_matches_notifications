import logging
import itertools as it

import pika
from sqlalchemy import inspect

from repository.database import session_factory, Base, engine
from repository.models import TeamsORM, RegionsORM


teams_data = {
        "EMEA": (
            "Team Heretics", "FNATIC", "Team Liquid",
            "Movistar KOI", "Karmine Corp", "Natus Vincere",
            "BBL Esports", "GIANTX", "Apeks", "Gentle Mates",
            "FUT Esports", "Team Vitality"
        ),
        "Pacific": (
            "BOOM Esports", "T1", "Global Esports", "Team Secret",
            "DetonatioN FocusMe", "Rex Regum Qeon", "ZETA DIVISION",
            "Nongshim RedForce", "Paper Rex", "TALON",
            "Gen.G", "DRX"
        ),
        "Americas": (
            "Evil Geniuses", "LOUD", "MIBR", "100 Thieves",
            "NRG Esports", "Cloud9", "2Game Esports",
            "FURIA", "KRÜ Esports", "Sentinels",
            "G2 Esports", "LEVIATÁN"
        ),
        "China": (
            "Xi Lai Gaming", "Wolves Esports", "TYLOO",
            "Titan Esports Club", "JDG Esports",
            "Dragon Ranger Gaming", "All Gamers", "Nova Esports",
            "Bilibili Gaming", "FunPlus Phoenix", "Trace Esports",
            "EDward Gaming"
        )
    }

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_db() -> None:
    inspector = inspect(engine)
    
    if not inspector.get_table_names():
        Base.metadata.create_all(engine)
    else:
        print("Tables already exist, skipping creation.")


    with session_factory() as session:
        if not session.query(TeamsORM).first():
            try:
                session.add_all(
                    [RegionsORM(name=region) for region in teams_data]
                    )
                
                for region in teams_data:
                    session.add_all(
                        [TeamsORM(name=team, region_name=region) for team in teams_data[region]]
                        )
                session.commit()
                
                print("Database has been initialized with data.")

            except Exception as err:
                session.rollback()
                print(f"Ошибка при инициализации данных: {err}")

        else:
            print("Data already exists, skipping initialization.")


def initialize_rabbit() -> None:
    params = pika.ConnectionParameters(host="rabbit", port=5672)
    with pika.BlockingConnection(params) as connection:
        with connection.channel() as channel:
            logger.info("Creating exchange and queues")            
            channel.exchange_declare(exchange="matches", exchange_type="topic", durable=True, auto_delete=False)
            
            for team in it.chain.from_iterable(teams_data.values()):
                channel.queue_declare(f"team.{team}.notifications", durable=True, auto_delete=False)

                channel.queue_bind(exchange="matches",
                                   queue=f"team.{team}.notifications",
                                   routing_key=f"match.{team}")
            
            logger.info("Exchange and queues have been created successfully") 


if __name__ == "__main__":
    initialize_db()
    initialize_rabbit()
