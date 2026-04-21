from config import MAX_POST_LENGTH
from datetime import datetime

CHANNEL_SIGNATURE = "\n—\n✍️ <a href=\"https://t.me/hpprow\">Ваш карманный HR</a>"

TREND_EMOJI = {"рост": "📈", "снижение": "📉", "стабильно": "➡️"}

DAY_CONTEXT = {
    0: "Понедельник — время ориентиров.",
    1: "Вторник. Рынок не ждёт.",
    2: "Середина недели. Самое время сверить часы.",
    3: "Четверг. До конца недели ещё есть время что-то изменить.",
    4: "Пятница. Неделя заканчивается — а рынок продолжает двигаться.",
    5: "Суббота. Пока другие отдыхают, ты смотришь на цифры.",
    6: "Воскресенье. Итоги — чтобы в понедельник стартовать точнее.",
}

def format_news_post(news: dict) -> str:
    impact_map = {
        "деньги": "💰 экономит деньги",
        "скорость": "⚡ ускоряет процессы",
        "качество": "🎯 улучшает качество найма",
    }
    impact_label = impact_map.get(news.get("impact", "").lower(), f"📌 {news.get('impact','')}")
    audience_map = {"hr": "HR-специалист", "рекрутер": "рекрутер", "руководитель": "руководитель", "бизнес": "владелец бизнеса"}
    audience_label = next((v for k, v in audience_map.items() if k in news.get("audience", "").lower()), news.get("audience", ""))
    post = (
        f"🧠 <b>{news.get('title', '')}</b>\n\n"
        f"{news.get('summary', '')}\n\n"
        f"Почему это важно прямо сейчас — {news.get('why_it_matters', '')}\n\n"
        f"Что делать: {news.get('hr_action', '')}\n\n"
        f"Кому читать: {audience_label} · {impact_label}\n"
        f"🔗 <a href=\"{news.get('source_url', '')}\">Подробнее</a>"
        f"{CHANNEL_SIGNATURE}\n\n"
        f"#AI_в_HR #автоматизация #hr_инструменты"
    )
    return post[:MAX_POST_LENGTH]

def format_salary_post(data: dict) -> str:
    spec = data.get("specialization", "")
    date = data.get("date", datetime.now().strftime("%d.%m.%Y"))
    insight = data.get("market_insight", "")
    hot_factor = data.get("hot_factor", "")
    hashtag = data.get("_hashtag", "рынок_труда")
    weekday = datetime.now().weekday()
    day_intro = DAY_CONTEXT.get(weekday, "")

    lines = [
        f"📊 <b>Зарплаты в Узбекистане: {spec}</b>",
        f"<i>{day_intro}</i>",
        f"<i>Данные на {date} · источник: hh.uz, OLX.uz</i>",
        "",
        "Смотрим, сколько платят — от входа до топа.",
        "",
    ]

    for pos in data.get("positions", []):
        trend_emoji = TREND_EMOJI.get(pos.get("trend", "").lower(), "➡️")
        skills = " · ".join(pos.get("key_skills", [])[:3])
        lines.append(f"<b>{pos.get('title', '')}</b>")
        lines.append(f"💰 {pos.get('salary_range_sum', '')}")
        if skills:
            lines.append(f"🔥 {skills}")
        lines.append(f"{trend_emoji} {pos.get('trend', '')} — {pos.get('comment', '')}")
        lines.append("")

    if insight:
        lines.append(f"💡 {insight}")
        lines.append("")
    if hot_factor:
        lines.append(f"⚡ Что поднимает цену: {hot_factor}")
        lines.append("")

    lines.append(CHANNEL_SIGNATURE)
    lines.append("")
    lines.append(f"#зарплаты_узбекистан #{hashtag} #рынок_труда")

    return "\n".join(lines)[:MAX_POST_LENGTH]
