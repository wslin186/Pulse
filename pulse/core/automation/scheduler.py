# pulse/core/automation/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler

class Scheduler:
    """轻量封装 APScheduler"""

    def __init__(self):
        self._sch = BackgroundScheduler()

    def add_daily_job(self, fn, time_str="09:00"):
        """每天指定时刻执行，如 '09:05'"""
        hour, minute = map(int, time_str.split(":"))
        self._sch.add_job(fn, trigger="cron", hour=hour, minute=minute)

    def start(self):
        self._sch.start()
