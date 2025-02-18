from .database import session_factory, Base, engine
from .models import TeamsORM, RegionsORM


def initialize_db():
    Base.metadata.create_all(engine)

    data = {
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

    with session_factory() as session:
        try:
            session.add_all([RegionsORM(name=region) for region in data])
            
            for region in data:
                session.add_all([TeamsORM(name=team, region_name=region) for team in data[region]])
            
            session.commit()

        except Exception as err:
            session.rollback()
            print(f"Ошибка при инициализации данных: {err}")

        else:
            print("База данных успешно инициализирована")


if __name__ == "__main__":
    initialize_db()