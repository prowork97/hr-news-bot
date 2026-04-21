import httpx
import logging
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, TEST_MODE

logger = logging.getLogger(__name__)

def send_to_telegram(text: str, disable_preview: bool = True) -> bool:
    if TEST_MODE:
        print("\n" + "="*50)
        print("[TEST MODE] Пост:")
        print(text)
        print("="*50 + "\n")
        return True
    try:
        resp = httpx.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHANNEL_ID,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": disable_preview,
            },
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("ok"):
            logger.info("Отправлено в Telegram")
            return True
        else:
            logger.error(f"Ошибка Telegram: {data}")
            return False
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")
        return False
