import re
from urllib.parse import urlparse
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

# ── Источники и чистка маркеров Perplexity ───────────────────────────────────

_CITATION_RE = re.compile(r"\s*\[\d+\](?:\s*\[\d+\])*")
_TELEGRAM_LIMIT = 4096


def strip_citations(text):
    """Убирает голые [1], [2][3][4] из строки текста Perplexity."""
    if not isinstance(text, str):
        return text
    text = _CITATION_RE.sub("", text)
    text = re.sub(r"\s+([.,:;!?»)])", r"\1", text)  # пробел перед пунктуацией
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def clean_markers_deep(obj):
    """Рекурсивно чистит [N] во всех строках распарсенного JSON (dict/list/str)."""
    if isinstance(obj, dict):
        return {k: clean_markers_deep(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_markers_deep(v) for v in obj]
    return strip_citations(obj)


def extract_sources(payload):
    """Достаёт реальные URL из ответа Perplexity (search_results → fallback citations)."""
    if not isinstance(payload, dict):
        return []
    sr = payload.get("search_results") or []
    if sr:
        return [{"url": s.get("url")} for s in sr if isinstance(s, dict) and s.get("url")]
    return [{"url": u} for u in (payload.get("citations") or []) if u]


def build_sources_block(sources, limit=5):
    """Собирает строку '📎 Источники: <a>домен</a> · ...' с дедупом по домену."""
    if not sources:
        return ""
    seen, uniq = set(), []
    for s in sources:
        url = s.get("url") if isinstance(s, dict) else s
        if not url:
            continue
        host = urlparse(url).netloc.replace("www.", "")
        if host and host not in seen:
            seen.add(host)
            uniq.append((host, url))
    uniq = uniq[:limit]
    if not uniq:
        return ""
    links = " · ".join(f'<a href="{u}">{h}</a>' for h, u in uniq)
    return f"\n\n📎 Источники: {links}"


def append_sources(post, sources):
    """Вставляет блок источников ПЕРЕД подписью канала, чтобы подпись осталась последней."""
    if not post:
        return post
    block = build_sources_block(sources)
    if not block:
        return post
    # не выходим за лимит Telegram
    if len(post) + len(block) > _TELEGRAM_LIMIT:
        return post
    idx = post.find("—\n✍️")
    if idx != -1:
        return post[:idx].rstrip() + block + "\n\n" + post[idx:]
    return post + block


# ── Форматтеры постов ────────────────────────────────────────────────────────

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
