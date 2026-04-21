from config import MAX_POST_LENGTH
from datetime import datetime

CHANNEL_SIGNATURE = "\n\n—\n✍️ [Ваш карманный HR](https://t.me/hpprow)"

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
    post = f"""🧠 *{news.get('title', '')}*

{news.get('summary', '')}

Почему это важно прямо сейчас — {news.get('why_it_matters', '')}

Что делать: {news.get('hr_action', '')}

Кому читать: {audience_label} · {impact_label}
🔗 [Подробнее]({news.get('source_url', '')}){CHANNEL_SIGNATURE}

#AI_в_HR #автоматизация #hr_инструменты"""
    return post[:MAX_POST_LENGTH]

def format_salary_post(data: dict) -> str:
    spec = data.get("specialization", "")
    date = data.get("date", datetime.now().strftime("%d.%m.%Y"))
    insight = data.get("market_insight", "")
    skills = data.get("hot_skills", [])
    source = data.get("source", "hh.uz")
    weekday = datetime.now().weekday()
    day_intro = DAY_CONTEXT.get(weekday, "")
    lines = [
        f"📊 *Зарплаты в Узбекистане: {spec}*",
        f"_{day_intro}_",
        f"_Данные актуальны на {date}_",
        "",
        "Смотрим, сколько сейчас платят — и куда движется рынок.",
        "",
    ]
    for lvl in data.get("levels", []):
        trend_emoji = TREND_EMOJI.get(lvl.get("trend", "").lower(), "➡️")
        lines.append(f"*{lvl.get('level', '')}*")
        lines.append(f"{lvl.get('salary_range', '')} · медиана {lvl.get('median', '')}")
        lines.append(f"{trend_emoji} {lvl.get('trend', '')} — {lvl.get('comment', '')}")
        lines.append("")
    lines.append(f"💡 {insight}")
    lines.append("")
    if skills:
        lines.append(f"🔥 Что поднимает цену: {' · '.join(f'`{s}`' for s in skills[:4])}")
        lines.append("")
    lines.append(f"_Источник: {source}_")
    lines.append(CHANNEL_SIGNATURE)
    lines.append("")
    lines.append(f"#зарплаты_узбекистан #рынок_труда #HR_аналитика")
    return "\n".join(lines)[:MAX_POST_LENGTH]
