import httpx
import json
import logging
from datetime import date, datetime
from config import PERPLEXITY_API_KEY

logger = logging.getLogger(__name__)

SPECIALIZATIONS = [
    ("HR / HRBP / Рекрутинг",                              "hr_рекрутинг"),
    ("Продажи B2B и B2C",                                   "продажи"),
    ("Финансы",                                             "финансы"),
    ("Маркетинг",                                           "маркетинг"),
    ("Операционный менеджмент",                             "операционный_менеджмент"),
    ("Customer Support / Call-центр",                       "customer_support"),
    ("Аккаунт-менеджеры / работа с клиентами",              "аккаунт_менеджмент"),
    ("Customer Success",                                    "customer_success"),
    ("IT-разработка",                                       "it_разработка"),
    ("Data / аналитики",                                    "data_аналитика"),
    ("Product Manager",                                     "product_management"),
    ("Project Manager",                                     "project_management"),
    ("UX/UI дизайнеры",                                     "ux_ui_дизайн"),
    ("Офис-менеджеры / администраторы",                     "офис_менеджмент"),
    ("Бизнес-ассистенты / личные ассистенты",               "бизнес_ассистенты"),
    ("Юристы",                                              "юристы"),
    ("Инженеры",                                            "инженеры"),
    ("Производственный персонал",                           "производство"),
    ("Логистика / Supply Chain",                            "логистика"),
    ("Ритейл",                                              "ритейл"),
    ("E-commerce",                                          "e_commerce"),
    ("Строительство",                                       "строительство"),
    ("Гостиницы / отели",                                   "гостиничный_бизнес"),
    ("Ресторанный бизнес",                                  "ресторанный_бизнес"),
    ("Учителя / преподаватели",                             "образование"),
    ("Тренеры / коучи / корпоративное обучение",            "обучение_и_коучинг"),
    ("CEO / Генеральные директора",                         "ceo"),
    ("Коммерческие директора",                              "коммерческий_директор"),
    ("Директора по маркетингу",                             "директор_по_маркетингу"),
    ("AI-специалисты / нейросети в бизнесе",                "ai_специалисты"),
]

SALARY_PROMPT_TEMPLATE = """
Ты — аналитик рынка труда Узбекистана.
Сегодня: {date}
Специализация: {spec}

Найди актуальные зарплаты в Узбекистане по специализации «{spec}».
Источники: hh.uz, OLX.uz, Telegram-каналы вакансий, LinkedIn.

Верни JSON (без markdown):
{{
  "specialization": "{spec}",
  "date": "{date}",
  "positions": [
    {{
      "title": "название должности",
      "salary_range_sum": "X млн – Y млн сум",
      "key_skills": ["навык1", "навык2"],
      "trend": "рост / стабильно / снижение",
      "comment": "1 предложение о спросе"
    }}
  ],
  "market_insight": "2-3 предложения об этом рынке в Узбекистане",
  "hot_factor": "что сильнее всего поднимает зарплату в этой сфере"
}}

Верни 4-6 должностей от низшей к высшей. Только JSON.
"""

def get_today_specialization() -> tuple[str, str]:
    day_of_cycle = (date.today() - date(2026, 4, 21)).days % 30
    return SPECIALIZATIONS[day_of_cycle]

def get_salary_analytics(retries: int = 3):
    spec, hashtag = get_today_specialization()
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
            data = json.loads(content)
            data["_hashtag"] = hashtag
            return data
        except Exception as e:
            logger.warning(f"Попытка {attempt+1}: {e}")
            if attempt == retries - 1:
                return None
