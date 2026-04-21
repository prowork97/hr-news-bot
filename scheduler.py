from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import logging
from storage import init_db
from main import (
    run_salary_job,
    run_news_job,
    run_hrtech_job,
    run_hot_topic_job,
    run_poll_job,
    run_weekly_digest_job,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TZ = pytz.timezone("Asia/Tashkent")


def start():
    init_db()
    scheduler = BlockingScheduler(timezone=TZ)

    # Пн 09:00 — зарплаты
    scheduler.add_job(run_salary_job, CronTrigger(day_of_week="mon", hour=9, minute=0, timezone=TZ), id="salary_monday")
    # Вт 09:00 — новость недели
    scheduler.add_job(run_news_job, CronTrigger(day_of_week="tue", hour=9, minute=0, timezone=TZ), id="news_tuesday")
    # Ср 09:00 — HR tech инструмент
    scheduler.add_job(run_hrtech_job, CronTrigger(day_of_week="wed", hour=9, minute=0, timezone=TZ), id="hrtech_wednesday")
    # Чт 09:00 — зарплаты
    scheduler.add_job(run_salary_job, CronTrigger(day_of_week="thu", hour=9, minute=0, timezone=TZ), id="salary_thursday")
    # Пт 09:00 — горячая тема
    scheduler.add_job(run_hot_topic_job, CronTrigger(day_of_week="fri", hour=9, minute=0, timezone=TZ), id="hot_topic_friday")
    # Сб 11:00 — опрос
    scheduler.add_job(run_poll_job, CronTrigger(day_of_week="sat", hour=11, minute=0, timezone=TZ), id="poll_saturday")
    # Вс 18:00 — дайджест недели
    scheduler.add_job(run_weekly_digest_job, CronTrigger(day_of_week="sun", hour=18, minute=0, timezone=TZ), id="digest_sunday")

    logger.info("Scheduler запущен:")
    logger.info("  Пн 09:00 — зарплаты")
    logger.info("  Вт 09:00 — новость недели")
    logger.info("  Ср 09:00 — HR tech")
    logger.info("  Чт 09:00 — зарплаты")
    logger.info("  Пт 09:00 — горячая тема")
    logger.info("  Сб 11:00 — опрос")
    logger.info("  Вс 18:00 — дайджест недели")
    scheduler.start()


if __name__ == "__main__":
    start()
