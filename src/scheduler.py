from datetime import timedelta

from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from repository.config import get_db_connection_url
from rabbit.producer import produce_message


class JobsScheduler:
    def __init__(self):
        jobstores = {
            "default": SQLAlchemyJobStore(url=get_db_connection_url(for_jobs=True))
        }
        
        self.scheduler = BackgroundScheduler()
        self.scheduler.configure(jobstores=jobstores, timezone=utc)
        self.scheduler.start()

    def add_matches(self, team_name, opponent, notify_time):
        self.scheduler.add_job(
            produce_message,
            args=(team_name, opponent),
            kwargs={"status": "через 1 час"},
            trigger=DateTrigger(run_date=notify_time),
            )

        self.scheduler.add_job(
            produce_message,
            args=(team_name, opponent),
            kwargs={"status": "прямо сейчас!"},
            trigger=DateTrigger(run_date=notify_time + timedelta(hours=1))
            )
        
    def daily_matches_check(self, crawler):
        self.scheduler.add_job(
            crawler.collect_matches_data,
            args=(self.scheduler, ),
            trigger=CronTrigger(
                hour=0,
                minute=0,
                second=20,
                ),
            )
