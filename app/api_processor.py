import logging
from datetime import datetime

import requests
from pytz import utc
from requests.exceptions import Timeout, ConnectionError, HTTPError

from src.repository.repository import Repository


repository = Repository()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MatchesDataProcessor:
    def __init__(self):
        self.api_endpoint = "https://vlrggapi.vercel.app/match?q=upcoming"
        self.teams = repository.list_all_teams()

    def get_vlr_api_response(self) -> list:
        response = requests.get(url=self.api_endpoint, timeout=5)
        response.raise_for_status()
        return response.json()

    def get_matches_data(self) -> list[tuple[str, str, datetime]]:
        try:
            api_response = self.get_vlr_api_response()
        except (ConnectionError, HTTPError, Timeout):
            print("Возникла проблема с соединением")
            return []
        except Exception as e:
            print(f"Возникла непредвиденная ошибка при обращении к API VLR.gg: {e}")
            return []
        
        upcoming_matches = api_response.get("data", {}).get("segments", [])
        target_matches = []

        for match_ in upcoming_matches:
            team1 = match_.get("team1")
            team2 = match_.get("team2")
            match_time = datetime.fromisoformat(match_.get("unix_timestamp"))

            if match_time is None:
                continue

            aware_match_time = match_time.replace(tzinfo=utc)

            if team1 in self.teams or team2 in self.teams:
                target_matches.append(
                    (team1, team2, aware_match_time)
                    )
                logger.info(f"Добавлен матч: {team1} vs {team2} в {aware_match_time}")
                
        return target_matches
