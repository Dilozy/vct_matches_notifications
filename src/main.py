import time
import logging
from datetime import timedelta, datetime

from pytz import utc

from src.services.scheduler import JobsScheduler
from src.services.vlr import MatchesDataProcessor


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = JobsScheduler()
matches_processor = MatchesDataProcessor()


def process_matches() -> None:
    matches = matches_processor.get_matches_data()
    matches.append(("BBL Esports", "FNATIC", datetime.now(utc) + timedelta(minutes=33)))
    matches.append(("BBL Esports", "G2 Esports", datetime.now(utc) + timedelta(minutes=4)))
    logger.info(f"Найдено матчей: {len(matches)}")
    
    for match_ in matches:
        scheduler.process_matches_notifications(*match_)


def main() -> None:
    scheduler.daily_matches_check(process_matches) 
    logger.info("Планировщик запущен. Ожидание задач...")

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Завершение работы планировщика...")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
