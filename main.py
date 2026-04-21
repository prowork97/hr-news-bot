import logging
from storage import init_db, save_news
from perplexity_client import get_hr_ai_news
from salary_client import get_salary_analytics, get_today_specialization
from deduplicator import is_duplicate
from formatter import format_news_post, format_salary_post
from publisher import send_to_telegram

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def run_news_job():
    logger.info("=== Новости AI/HR ===")
    news_list = get_hr_ai_news()
    if not news_list:
        logger.warning("Новостей не получено")
        return
    published = 0
    for news in news_list:
        title = news.get("title", "")
        url = news.get("source_url", "")
        if is_duplicate(title, url):
            logger.info(f"Дубликат: {title[:50]}")
            continue
        post = format_news_post(news)
        if send_to_telegram(post):
            save_news(title, url)
            published += 1
    logger.info(f"Опубликовано: {published}/{len(news_list)}")

def run_salary_job():
    logger.info("=== Зарплатная аналитика ===")
    spec, day = get_today_specialization()
    logger.info(f"Специализация: {spec}")
    data = get_salary_analytics()
    if not data:
        logger.warning("Данные не получены")
        return
    post = format_salary_post(data)
    send_to_telegram(post)

if __name__ == "__main__":
    init_db()
    run_news_job()
    run_salary_job()
