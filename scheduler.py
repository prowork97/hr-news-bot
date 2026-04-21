from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import logging
from storage import init_db
from main import run_news_job, run_salary_job

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TZ = pytz.timezone("Asia/Tashkent")

def start():
    init_db()
    scheduler = BlockingScheduler(timezone=TZ)
    scheduler.add_job(run_news_job, CronTrigger(hour=8, minute=30, timezone=TZ), id="news_morning")
    scheduler.add_job(run_news_job, CronTrigger(hour=13, minute=0, timezone=TZ), id="news_afternoon")
    scheduler.add_job(run_salary_job, CronTrigger(hour=19, minute=0, timezone=TZ), id="salary_evening")
    logger.info("Scheduler запущен: 08:30, 13:00 (новости) · 19:00 (зарплаты)")
    scheduler.start()

if __name__ == "__main__":
    start()
