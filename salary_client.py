import httpx
import json
import logging
from datetime import datetime
from config import PERPLEXITY_API_KEY

logger = logging.getLogger(__name__)

SPECIALIZATIONS = [
    ("IT / разработка", "Пн"),
    ("Продажи / коммерция", "Вт"),
    ("Маркетинг / SMM / digital", "Ср"),
    ("HR / рекрутинг", "Чт"),
    ("Финансы / бухгалтерия", "Пт"),
    ("Топ-менеджмент / директора", "Сб"),
    ("Итоги недели / рейтинг вакансий", "Вс"),
]

SALARY_PROMPT_TEMPLATE = """
Ты — аналитик рынка труда Узбекистана.
Сегодня: {date}
Специализация: {spec}

Собери актуальные данные о зарплатах в Узбекистане по специализации «{spec}».
Используй данные с hh.uz, LinkedIn, местных агентств.

Верни строго JSON (без markdown):
{{
  "specialization": "{spec}",
  "date": "{date}",
  "currency_note": "зарплаты указаны в USD, медианные значения",
  "levels": [
    {{"level": "Junior / начальный", "salary_range": "$XXX–XXX", "median": "$XXX", "trend": "рост / стабильно / снижение", "comment": "комментарий"}},
    {{"level": "Middle / специалист", "salary_range": "$XXX–XXX", "median": "$XXX", "trend": "рост / стабильно / снижение", "comment": "комментарий"}},
    {{"level": "Senior / руководитель", "salary_range": "$XXX–XXX", "median": "$XXX", "trend": "рост / стабильно / снижение", "comment": "комментарий"}}
  ],
  "market_insight": "1-2 предложения о тренде",
  "hot_skills": ["навык1", "навык2", "навык3"],
  "source": "hh.uz / LinkedIn"
}}
"""

def get_today_specialization():
    weekday = datetime.now().weekday()
    return SPECIALIZATIONS[weekday]

def get_salary_analytics(retries: int = 3):
    spec, day = get_today_specialization()
    date_str = datetime.now().strftime("%d.%m.%Y")
    prompt = SALARY_PROMPT_TEMPLATE.format(spec=spec, date=date_str)
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
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1500,
                    "temperature": 0.2,
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
            logger.warning(f"Попытка {attempt+1}: {e}")
            if attempt == retries - 1:
                return None
