from datetime import timedelta, datetime

import requests
from pytz import utc
from requests.exceptions import Timeout, ConnectionError, HTTPError

from repository.repository import Repository


repository = Repository()


class MatchesDataCrawler:
    def __init__(self):
        self.api_endpoint = "https://vlrggapi.vercel.app/match?q=upcoming"
        self.teams = repository.list_all_teams()

    def get_vlr_api_response(self):
        response = requests.get(url=self.api_endpoint, timeout=5)
        response.raise_for_status()
        return response.json()

    def get_matches_data(self):
        try:
            api_response = self.get_vlr_api_response()
        except (ConnectionError, HTTPError, Timeout):
            print("Возникла проблема с соединением")
        except Exception as e:
            print(f"Возникла непредвиденная ошибка при обращении к API VLR.gg: {e}")
        
        upcoming_matches = api_response.get("data").get("segments")

        target_matches = []

        if upcoming_matches is not None:
            for match_ in upcoming_matches:
                match_utc_time = datetime.fromisoformat(match_.get("unix_timestamp")) \
                                         .replace(tzinfo=utc)
                time_diff = datetime.now(utc) - match_utc_time
                
                notify_time = match_utc_time - timedelta(hours=1)

                if (match_.get("team1") in self.teams) and time_diff.days == 0:
                    target_matches.append(
                        (match_.get("team1"), match_.get("team2"), notify_time)
                        )
                
                if match_.get("team2") in self.teams and time_diff.days == 0:
                    target_matches.append(
                        (match_.get("team2"), match_.get("team1"), notify_time)
                        )
    
        return target_matches
    
    def collect_matches_data(self, scheduler):
        target_matches = self.get_matches_data()

        for match_data in target_matches:
            scheduler.add_match(*match_data)
