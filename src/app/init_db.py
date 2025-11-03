import logging

from sqlalchemy import inspect

from src.db.connect import session_factory, engine
from src.db.models import Team, Region, Base


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
        if not session.query(Team).first():
            try:
                session.add_all(
                    [Region(name=region) for region in teams_data]
                    )
                
                for region in teams_data:
                    session.add_all(
                        [Team(name=team, region_name=region) for team in teams_data[region]]
                        )
                session.commit()
                
                print("Database has been initialized with data.")

            except Exception as err:
                session.rollback()
                print(f"Data initialization error: {err}")

        else:
            print("Data already exists, skipping initialization.")


if __name__ == "__main__":
    initialize_db()
