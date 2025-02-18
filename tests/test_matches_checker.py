from datetime import datetime, timedelta

import pytest
import requests
from requests.exceptions import HTTPError
from contextlib import nullcontext as does_not_raise
from unittest.mock import patch

from src.crawler import MatchesDataCrawler


def mock_correct_api_json_response():
    response = {
        'data': {
            'status': 200, 'segments': [
                {
                    'team1': 'T1', 'team2': 'DRX', 'flag1': 'flag_kr', 'flag2': 'flag_kr', 'time_until_match': '21h 11m from now', 'match_series': 'Main Event: Upper Final', 'match_event': 'Champions Tour 2025: Pacific Kickoff', 'unix_timestamp': '2025-02-07 08:00:00', 'match_page': 'https://www.vlr.gg/430524/t1-vs-drx-champions-tour-2025-pacific-kickoff-ubf'
                },
                {
                    'team1': 'Sentinels', 'team2': 'G2 Esports', 'flag1': 'flag_us', 'flag2': 'flag_us', 'time_until_match': '11h 11m from now', 'match_series': 'Main Event: Upper Final', 'match_event': 'Champions Tour 2025: Americas Kickoff', 'unix_timestamp': '2025-02-06 22:00:00', 'match_page': 'https://www.vlr.gg/428001/sentinels-vs-g2-esports-champions-tour-2025-americas-kickoff-ubf'
                 }
            ]
            }
        }
    return response


def mock_empty_api_json_response():
    response = {
        'data': {
            'status': 200, 'segments': []
            }
        }
    return response


def mock_incorrect_api_json_response():
    response = {'data': {}}
    return response


class TestMatchesDataCrawler:
    @pytest.mark.parametrize(
        "api_endpoint, expectation",
        [
            ("https://vlrggapi.vercel.app/match?q=upcoming", does_not_raise()),
            ("https://vlrggapihghg.vercel.app/match?q=upcoming", pytest.raises(HTTPError)),
            ("112233", pytest.raises(Exception)),
        ]
    )
    def test_get_vlr_api_response(self, api_endpoint, expectation):
        crawler = MatchesDataCrawler()
        crawler.api_endpoint = api_endpoint
        with expectation:
            response = requests.get(url=api_endpoint, timeout=5)
            assert crawler.get_vlr_api_response() == response.json()

    @pytest.mark.parametrize(
            "mock_api_json_response",
            [
                (mock_correct_api_json_response()),
                (mock_empty_api_json_response()),
                (mock_incorrect_api_json_response())

            ]
    )
    @patch("src.matches_checker.MatchesDataCrawler.get_vlr_api_response")
    def test_process_matches_data(self, mock_get_vlr_api_response, mock_api_json_response):
        mock_get_vlr_api_response.return_value = mock_api_json_response

        crawler = MatchesDataCrawler()

        processed_result = crawler.process_matches_data()

        if mock_api_json_response["data"].get("segments"):
            expected_result = [
                ("T1 vs DRX", datetime.fromisoformat("2025-02-07 08:00:00") - timedelta(hours=1)),
                ("Sentinels vs G2 Esports", datetime.fromisoformat("2025-02-06 22:00:00") - timedelta(hours=1)),
            ]
        
        else:
            expected_result = []

        assert expected_result == processed_result
