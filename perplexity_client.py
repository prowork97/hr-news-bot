import httpx
import json
import logging
from config import PERPLEXITY_API_KEY

logger = logging.getLogger(__name__)

NEWS_PROMPT = """
Ты — редактор Telegram-канала «Ваш карманный HR».

Найди за последние 24 часа важные новости по темам:
- AI в HR и рекрутинге
- AI в управлении и бизнесе
- Автоматизация HR-процессов
- AI-ассистенты для бизнеса

ФИЛЬТР: оставляй только новости, которые влияют на деньги, скорость или качество работы.

Верни строго JSON-массив (без пояснений, без markdown):
[
  {
    "title": "заголовок",
    "summary": "краткое описание 2-3 предложения",
    "why_it_matters": "почему важно для HR/бизнеса",
    "hr_action": "конкретное действие",
    "audience": "HR / рекрутер / руководитель",
    "impact": "деньги / скорость / качество",
    "source_url": "ссылка"
  }
]

Верни 3-5 новостей. Только JSON.
"""

def get_hr_ai_news(retries: int = 3) -> list[dict]:
    for attempt in range(retries):
        try:
            resp = httpx.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "sonar-pro",
                    "messages": [{"role": "user", "content": NEWS_PROMPT}],
                    "max_tokens": 2000,
                    "temperature": 0.3,
                },
                timeout=30.0,
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            news_list = json.loads(content)
            logger.info(f"Получено новостей: {len(news_list)}")
            return news_list
        except Exception as e:
            logger.warning(f"Попытка {attempt+1} не удалась: {e}")
            if attempt == retries - 1:
                return []
