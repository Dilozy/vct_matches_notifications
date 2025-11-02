from datetime import timedelta, datetime
from typing import Any, Callable

from pytz import utc
from apscheduler.job import Job
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from src.common.repository.config import get_db_connection_url
from src.common.repository.database import engine
from src.common.rabbit.producer import produce_message


class MatchCountdown:
    def __init__(self, match_time: datetime) -> None:
        self.match_time = match_time
    
    @staticmethod
    def _get_reminder_time_diff(match_time: datetime) -> timedelta:
        time_diff = match_time - datetime.now(utc)
        
        return timedelta(minutes=30) if int(time_diff.total_seconds()) >= 1800 else time_diff

    @staticmethod
    def _get_minute_declension(minutes: int) -> str:
        if minutes % 10 == 1 and minutes % 100 != 11:
            return "минуту"
        elif 2 <= minutes % 10 <= 4 and not (12 <= minutes % 100 <= 14):
            return "минуты"
        else:
            return "минут"


    def _get_status_msg(self) -> str:
        time_diff = self._get_reminder_time_diff(self.match_time)
        full_minutes = int(time_diff.total_seconds()) // 60
        return f"через {full_minutes} {self._get_minute_declension(full_minutes)}"

    @property
    def status(self) -> str:
        """Возвращает статус напоминания в виде строки (например, 'через 5 минут')."""
        return self._get_status_msg()
    
    @property
    def time_diff(self) -> timedelta:
        """Возвращает разницу во времени до матча в виде timedelta."""
        return self._get_reminder_time_diff(self.match_time)


class JobsScheduler:
    def __init__(self) -> None:
        jobstores = {
            "default": SQLAlchemyJobStore(
                url=get_db_connection_url(),
                engine=engine
                )
        }
        
        self.scheduler = BackgroundScheduler()
        self.scheduler.configure(jobstores=jobstores, timezone=utc)
        self.scheduler.start()

    def _reshedule_notification_job(self, job: Job, match_data: dict[str, Any]) -> None:
        team1 = match_data["team1"]
        team2 = match_data["team2"]
        new_match_time = match_data["match_time"]
        new_reminder_time = match_data["reminder_time"]
        countdown_status = match_data["countdown_status"]
        countdown_seconds = match_data["countdown_seconds"]
        
        if countdown_seconds > 60:
            match_reminder_job = self.scheduler.get_job(f"{team1}_{team2}_reminder")

            if match_reminder_job:
                self.scheduler.modify_job(
                    match_reminder_job.id,
                    jobstore="default",
                    trigger=DateTrigger(run_date=new_reminder_time + timedelta(seconds=10),
                                        timezone=utc),
                    kwargs={"status": countdown_status},
                )
            
        self.scheduler.modify_job(
            job.id,
            jobstore="default",
            trigger=DateTrigger(run_date=new_match_time + timedelta(seconds=10),
                                timezone=utc),
                )
        
    def _create_notification_job(self, match_data: dict) -> None:
        team1 = match_data["team1"]
        team2 = match_data["team2"]
        match_time = match_data["match_time"]
        reminder_time = match_data["reminder_time"]
        countdown_status = match_data["countdown_status"]
        countdown_seconds = match_data["countdown_seconds"]
        
        if countdown_seconds > 60:
            self.scheduler.add_job(
                produce_message,
                args=(team1, team2),
                kwargs={"status": countdown_status},
                trigger=DateTrigger(run_date=reminder_time + timedelta(seconds=10),
                                    timezone=utc),
                id=f"{team1}_{team2}_reminder"
            )

        self.scheduler.add_job(
            produce_message,
            args=(team1, team2),
            kwargs={"status": "прямо сейчас!"},
            trigger=DateTrigger(run_date=match_time + timedelta(seconds=10),
                                timezone=utc),
            id=f"{team1}_{team2}_start"
        )

    def process_matches_notifications(self, team1: str, team2: str, match_time: datetime) -> None:
        countdown = MatchCountdown(match_time)

        match_data = {"team1": team1,
                      "team2": team2,
                      "match_time": match_time,
                      "reminder_time": match_time - countdown.time_diff,
                      "countdown_status": countdown.status,
                      "countdown_seconds": int(countdown.time_diff.total_seconds())}
        
        if (match_start_job := self.scheduler.get_job(f"{team1}_{team2}_start")):
            if match_start_job.trigger.run_date != match_time:
                self._reshedule_notification_job(match_start_job,
                                                 match_data)
        else:
            self._create_notification_job(match_data)

    @staticmethod
    def _calculate_start_date() -> datetime:
        now = datetime.now(utc)
        current_minute = now.minute
        if current_minute < 30:
            return now.replace(minute=30, second=0, microsecond=0)
        else:
            return (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

    def daily_matches_check(self, collect_matches_func: Callable[[], None]) -> None:
        if not self.scheduler.get_job(job_id="daily_matches_check"):
            start_date = self._calculate_start_date() + timedelta(seconds=20)
            self.scheduler.add_job(
                collect_matches_func,
                trigger=IntervalTrigger(minutes=30,
                                        start_date=start_date,
                                        timezone=utc),
                id="daily_matches_check"
            )

    def shutdown(self):
        self.scheduler.shutdown()
