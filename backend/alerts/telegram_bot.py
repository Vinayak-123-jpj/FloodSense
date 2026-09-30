"""Telegram Multilingual Bot & Alert Dispatcher.

Handles English & Hindi flood warning message formatting, Telegram API POST dispatching,
and graceful fallback to the visible in-app Alert Outbox when no Telegram token is configured.
"""

import requests
from backend.config import settings

HINDI_RISK_MAP = {
    "Green": "सुरक्षित (Green)",
    "Yellow": "सचेत (Yellow)",
    "Orange": "चेतावनी (Orange)",
    "Red": "गंभीर खतरा (Red)"
}

HINDI_ACTION_MAP = {
    "Green": "सामान्य स्थिति। जल स्तर की निगरानी जारी रखें।",
    "Yellow": "सतर्क रहें। निचले इलाकों में पानी भरने की संभावना है।",
    "Orange": "तैयार रहें! आवश्यक सामान के साथ सुरक्षित स्थानों पर जाएँ।",
    "Red": "तत्काल निकासी! तुरंत उच्च स्थान या राहत शिविर में जाएँ।"
}

ENGLISH_ACTION_MAP = {
    "Green": "Normal conditions. Continue standard monitoring.",
    "Yellow": "Be aware. Low-lying areas may experience minor waterlogging.",
    "Orange": "Be prepared! Pack essential documents and prepare for evacuation.",
    "Red": "Immediate Evacuation! Proceed immediately to designated high ground or relief shelters."
}

def format_alert_message(
    station_name: str,
    river: str,
    risk_level: str,
    water_level_m: float,
    danger_level_m: float,
    reason: str,
    evacuation_url: str,
    language: str = "en"
) -> str:
    """Formats English or Hindi alert message text for Telegram dispatch."""
    if language == "hi":
        risk_str = HINDI_RISK_MAP.get(risk_level, risk_level)
        action_str = HINDI_ACTION_MAP.get(risk_level, "सुरक्षित स्थान पर जाएं।")
        msg = (
            f"🚨 *बाढ़ चेतावनी अपडेट*\n\n"
            f"📍 *स्टेशन*: {station_name} ({river})\n"
            f"⚠️ *जोखिम स्तर*: {risk_str}\n"
            f"📊 *वर्तमान जल स्तर*: {water_level_m:.2f} मी (खतरा: {danger_level_m:.2f} मी)\n"
            f"💡 *मुख्य कारण*: {reason}\n"
            f"🏃 *अनुशंसित कार्रवाई*: {action_str}\n\n"
            f"🗺️ [निकासी मार्ग मानचित्र]({evacuation_url})"
        )
    else:
        action_str = ENGLISH_ACTION_MAP.get(risk_level, "Evacuate to safety.")
        msg = (
            f"🚨 *FLOOD WARNING ALERT*\n\n"
            f"📍 *Station*: {station_name} ({river})\n"
            f"⚠️ *Risk Level*: {risk_level.upper()}\n"
            f"📊 *Water Level*: {water_level_m:.2f}m (Danger Mark: {danger_level_m:.2f}m)\n"
            f"💡 *Primary Driver*: {reason}\n"
            f"🏃 *Action Required*: {action_str}\n\n"
            f"🗺️ [Evacuation Route Map]({evacuation_url})"
        )
    return msg

def send_telegram_alert(message_text: str) -> bool:
    """Dispatches Telegram alert via HTTP POST API call if token is configured."""
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        print("[Telegram Bot] No token set in .env. Alert logged exclusively to visible In-App Outbox.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "Markdown"
    }

    try:
        res = requests.post(url, json=payload, timeout=5.0)
        if res.status_code == 200:
            print("[Telegram Bot] Successfully delivered Telegram alert message!")
            return True
        else:
            print(f"[Telegram Bot Error] Telegram API returned code {res.status_code}: {res.text}")
            return False
    except Exception as e:
        print(f"[Telegram Bot Exception] {e}")
        return False
