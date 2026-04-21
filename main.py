import httpx
import json
import logging
from datetime import datetime
from storage import init_db, save_news
from salary_client import get_salary_analytics, get_today_specialization
from deduplicator import is_duplicate
from formatter import format_news_post, format_salary_post
from publisher import send_to_telegram, send_poll
from config import PERPLEXITY_API_KEY

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CHANNEL_SIGNATURE = '\n—\n✍️ <a href="https://t.me/hpprow">Ваш карманный HR</a>'


def _perplexity(prompt: str, max_tokens: int = 1500, temperature: float = 0.3) -> dict | list | None:
    for attempt in range(3):
        try:
            resp = httpx.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "sonar-pro",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                timeout=30.0,
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except Exception as e:
            logger.warning(f"Perplexity попытка {attempt+1}: {e}")
    return None


# ── Понедельник / Четверг 09:00 ──────────────────────────────────────────────

def run_salary_job():
    logger.info("=== Зарплатная аналитика ===")
    spec, _ = get_today_specialization()
    logger.info(f"Специализация: {spec}")
    data = get_salary_analytics()
    if not data:
        logger.warning("Данные не получены")
        return
    post = format_salary_post(data)
    send_to_telegram(post)


# ── Вторник 09:00 ─────────────────────────────────────────────────────────────

NEWS_PROMPT = """
Найди ОДНУ самую важную новость за последние 48 часов по теме AI в HR и бизнесе.
Критерий важности: максимальное влияние на деньги или процессы в компании.

Верни JSON:
{
  "title": "заголовок",
  "what_happened": "что произошло — 2 предложения",
  "why_big_deal": "почему это меняет правила — 2 предложения",
  "uzbekistan_angle": "как это касается рынка Узбекистана конкретно",
  "action_this_week": "что сделать HR или руководителю прямо на этой неделе",
  "contrarian_take": "неожиданный взгляд на новость — 1 провокационное предложение",
  "source_url": "ссылка"
}
"""

def run_news_job():
    logger.info("=== Новость недели ===")
    data = _perplexity(NEWS_PROMPT, max_tokens=1000)
    if not data:
        logger.warning("Новость не получена")
        return
    title = data.get("title", "")
    url = data.get("source_url", "")
    if is_duplicate(title, url):
        logger.info(f"Дубликат: {title[:50]}")
        return
    post = (
        f"🧠 <b>{title}</b>\n\n"
        f"{data.get('what_happened', '')}\n\n"
        f"<b>Почему это важно:</b>\n{data.get('why_big_deal', '')}\n\n"
        f"<b>Узбекистан:</b>\n{data.get('uzbekistan_angle', '')}\n\n"
        f"<b>Что делать на этой неделе:</b>\n{data.get('action_this_week', '')}\n\n"
        f"💬 <i>{data.get('contrarian_take', '')}</i>\n\n"
        f"🔗 <a href=\"{url}\">Читать полностью</a>"
        f"{CHANNEL_SIGNATURE}\n\n"
        f"#AI_в_HR #тренды #hr_инструменты"
    )
    if send_to_telegram(post):
        save_news(title, url)


# ── Среда 09:00 ───────────────────────────────────────────────────────────────

HRTECH_PROMPT = """
Ты — редактор HR-канала. Найди один конкретный AI-инструмент или HR-tech продукт,
который стал популярным или получил обновление за последние 2 недели.

Верни JSON:
{
  "tool_name": "название инструмента",
  "category": "категория (ATS / онбординг / аналитика / рекрутинг / и т.д.)",
  "what_it_does": "что делает — 2 предложения",
  "key_feature": "главная фича которая выделяет его",
  "use_case": "конкретный сценарий использования в компании",
  "price_info": "информация о цене / есть ли free tier",
  "uzbekistan_fit": "подходит ли для узбекского рынка и почему",
  "tool_url": "ссылка на инструмент"
}
"""

def run_hrtech_job():
    logger.info("=== HR Tech инструмент ===")
    data = _perplexity(HRTECH_PROMPT, max_tokens=1000)
    if not data:
        logger.warning("Данные не получены")
        return
    post = (
        f"🛠 <b>{data.get('tool_name', '')} — {data.get('category', '')}</b>\n\n"
        f"{data.get('what_it_does', '')}\n\n"
        f"<b>Главная фича:</b> {data.get('key_feature', '')}\n\n"
        f"<b>Как использовать:</b> {data.get('use_case', '')}\n\n"
        f"<b>Цена:</b> {data.get('price_info', '')}\n\n"
        f"<b>Узбекистан:</b> {data.get('uzbekistan_fit', '')}\n\n"
        f"🔗 <a href=\"{data.get('tool_url', '')}\">Попробовать</a>"
        f"{CHANNEL_SIGNATURE}\n\n"
        f"#hrtech #инструменты #автоматизация_HR"
    )
    send_to_telegram(post)


# ── Пятница 09:00 ─────────────────────────────────────────────────────────────

HOT_TOPIC_PROMPT = """
Ты — редактор самого актуального и свежего HR-канала в Узбекистане.

Найди или сформулируй одну актуальную тему о рынке труда Узбекистана которая:
- вызовет споры или эмоции у HR и руководителей
- основана на реальных данных или тренде
- актуальна прямо сейчас

Верни JSON:
{
  "hook": "яркий заголовок — вопрос или утверждение до 10 слов",
  "thesis": "главная мысль — 2-3 предложения с фактами",
  "argument_for": "аргумент ЗА тезис",
  "argument_against": "аргумент ПРОТИВ тезиса",
  "uzbekistan_reality": "как это реально выглядит в узбекских компаниях",
  "call_to_action": "вопрос к аудитории для комментариев"
}
"""

def run_hot_topic_job():
    logger.info("=== Горячая тема ===")
    data = _perplexity(HOT_TOPIC_PROMPT, max_tokens=1000)
    if not data:
        logger.warning("Данные не получены")
        return
    post = (
        f"🔥 <b>{data.get('hook', '')}</b>\n\n"
        f"{data.get('thesis', '')}\n\n"
        f"<b>Аргумент за:</b> {data.get('argument_for', '')}\n\n"
        f"<b>Аргумент против:</b> {data.get('argument_against', '')}\n\n"
        f"<b>Реальность Узбекистана:</b>\n{data.get('uzbekistan_reality', '')}\n\n"
        f"💬 {data.get('call_to_action', '')}\n\n"
        f"Пишите в комментарии 👇"
        f"{CHANNEL_SIGNATURE}\n\n"
        f"#мнение #рынок_труда #HR_Узбекистан"
    )
    send_to_telegram(post)


# ── Суббота 11:00 ─────────────────────────────────────────────────────────────

POLL_PROMPT = """
Придумай один острый опрос для HR-специалистов и руководителей Узбекистана.
Тема: рынок труда, зарплаты, найм, управление командой.

Верни JSON:
{
  "question": "вопрос для опроса до 15 слов",
  "options": ["вариант 1", "вариант 2", "вариант 3", "вариант 4"]
}
"""

def run_poll_job():
    logger.info("=== Опрос ===")
    data = _perplexity(POLL_PROMPT, max_tokens=300, temperature=0.5)
    if not data:
        logger.warning("Данные не получены")
        return
    question = data.get("question", "")
    options = data.get("options", [])
    if not question or len(options) < 2:
        logger.warning("Некорректные данные опроса")
        return
    send_poll(question, options[:4])


# ── Воскресенье 18:00 ─────────────────────────────────────────────────────────

def _weekly_digest_prompt() -> str:
    date_str = datetime.now().strftime("%d.%m.%Y")
    return f"""
Ты — редактор HR-канала. Сегодня воскресенье {date_str}.

Найди 3 главных инсайта этой недели по теме:
- рынок труда Узбекистана
- AI и автоматизация в HR
- зарплатные тренды

Верни JSON:
{{
  "week_headline": "главная тема недели — одна фраза",
  "insights": [
    {{"number": 1, "title": "инсайт", "description": "2 предложения"}},
    {{"number": 2, "title": "инсайт", "description": "2 предложения"}},
    {{"number": 3, "title": "инсайт", "description": "2 предложения"}}
  ],
  "next_week_preview": "что важного ждёт рынок на следующей неделе"
}}
"""

def run_weekly_digest_job():
    logger.info("=== Дайджест недели ===")
    data = _perplexity(_weekly_digest_prompt(), max_tokens=1200)
    if not data:
        logger.warning("Данные не получены")
        return
    date_str = datetime.now().strftime("%d.%m.%Y")
    insights = data.get("insights", [])

    lines = [
        f"📋 <b>{data.get('week_headline', '')}</b>",
        f"<i>Итоги недели · {date_str}</i>",
        "",
        "<b>3 инсайта которые стоит знать:</b>",
        "",
    ]
    numbers = ["1️⃣", "2️⃣", "3️⃣"]
    for i, insight in enumerate(insights[:3]):
        lines.append(f"{numbers[i]} <b>{insight.get('title', '')}</b>")
        lines.append(insight.get("description", ""))
        lines.append("")

    lines.append(f"<b>На следующей неделе:</b>")
    lines.append(data.get("next_week_preview", ""))
    lines.append("")
    lines.append("Сохрани этот пост — пригодится в понедельник 👆")
    lines.append(CHANNEL_SIGNATURE)
    lines.append("")
    lines.append("#итоги_недели #HR_аналитика #рынок_труда")

    send_to_telegram("\n".join(lines))


if __name__ == "__main__":
    init_db()
    run_news_job()
    run_salary_job()
