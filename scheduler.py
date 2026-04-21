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

    # Каждый день 09:00 — зарплатная аналитика (30 специализаций, бесконечный цикл)
    scheduler.add_job(run_salary_job, CronTrigger(hour=9, minute=0, timezone=TZ), id="salary_daily")
    # Вт 09:00 — новость недели (дополнительно к зарплатам)
    scheduler.add_job(run_news_job, CronTrigger(day_of_week="tue", hour=10, minute=0, timezone=TZ), id="news_tuesday")
    # Ср 09:00 — HR tech инструмент
    scheduler.add_job(run_hrtech_job, CronTrigger(day_of_week="wed", hour=10, minute=0, timezone=TZ), id="hrtech_wednesday")
    # Пт 09:00 — горячая тема
    scheduler.add_job(run_hot_topic_job, CronTrigger(day_of_week="fri", hour=10, minute=0, timezone=TZ), id="hot_topic_friday")
    # Сб 11:00 — опрос
    scheduler.add_job(run_poll_job, CronTrigger(day_of_week="sat", hour=11, minute=0, timezone=TZ), id="poll_saturday")
    # Вс 18:00 — дайджест недели
    scheduler.add_job(run_weekly_digest_job, CronTrigger(day_of_week="sun", hour=18, minute=0, timezone=TZ), id="digest_sunday")

    logger.info("Scheduler запущен:")
    logger.info("  Каждый день 09:00 — зарплаты (30 специализаций, бесконечный цикл)")
    logger.info("  Вт 10:00 — новость недели")
    logger.info("  Ср 10:00 — HR tech")
    logger.info("  Пт 10:00 — горячая тема")
    logger.info("  Сб 11:00 — опрос")
    logger.info("  Вс 18:00 — дайджест недели")
    scheduler.start()


if __name__ == "__main__":
    start()
