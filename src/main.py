import time

from ..src.scheduler import JobsScheduler
from ..src.crawler import MatchesDataCrawler


def main():
    scheduler = JobsScheduler()
    crawler = MatchesDataCrawler()

    scheduler.daily_matches_check(crawler)

    try:
        while True:
            time.sleep(1)
    except(KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    main()
