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

MALAYALAM_RISK_MAP = {
    "Green": "സാധാരണ (Green)",
    "Yellow": "ജാഗ്രത (Yellow)",
    "Orange": "മുന്നറിയിപ്പ് (Orange)",
    "Red": "തീവ്ര അപായസാധ്യത (Red)"
}

MALAYALAM_ACTION_MAP = {
    "Green": "സാധാരണ നിലവാരം. നിരീക്ഷണം തുടരുക.",
    "Yellow": "ജാഗ്രത പാലിക്കുക. താഴ്ന്ന പ്രദേശങ്ങളിൽ വെള്ളക്കെട്ടിന് സാധ്യത.",
    "Orange": "സജ്ജരായിരിക്കുക! അടിയന്തര സാധനങ്ങളുമായി സുരക്ഷിത സ്ഥാനങ്ങളിലേക്ക് മാറാൻ തയ്യാറെടുക്കുക.",
    "Red": "ഉടൻ മാറിത്താമസിക്കുക! സുരക്ഷിത കേന്ദ്രങ്ങളിലേക്കോ ക്യാമ്പുകളിലേക്കോ ഉടനടി മാറുക."
}

ASSAMESE_RISK_MAP = {
    "Green": "স্বাভাবিক (Green)",
    "Yellow": "সতর্ক (Yellow)",
    "Orange": "সাঁৱধান (Orange)",
    "Red": "জৰুৰী বিপদ (Red)"
}

ASSAMESE_ACTION_MAP = {
    "Green": "স্বাভাৱিক অৱস্থা। জলস্তৰ নিৰীক্ষণ অব্যাহত ৰাখক।",
    "Yellow": "সজাগ হওক। নামনি অঞ্চলত পানী জমা হ'ব পাৰে।",
    "Orange": "প্ৰস্তুত থাকক! প্ৰয়োজনীয় সামগ্ৰীৰ সৈতে সুৰক্ষিত স্থানলৈ যোৱাৰ প্ৰস্তুতি চলাওক।",
    "Red": "তাত্ক্ষণিক স্থানান্তৰ! লগে লগে সুৰক্ষিত উচ্চ স্থান বা আশ্ৰয় শিবিৰলৈ যাওক।"
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
    """Formats English, Hindi, Malayalam, or Assamese alert message text for Telegram dispatch.
    Note: Non-English translations are draft templates requiring native-speaker review.
    """
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
    elif language == "ml":
        risk_str = MALAYALAM_RISK_MAP.get(risk_level, risk_level)
        action_str = MALAYALAM_ACTION_MAP.get(risk_level, "സുരക്ഷിത സ്ഥാനത്തേക്ക് മാറുക.")
        msg = (
            f"🚨 *പ്രളയ മുന്നറിയിപ്പ് നോട്ടിഫിക്കേഷൻ*\n\n"
            f"📍 *സ്റ്റേഷൻ*: {station_name} ({river})\n"
            f"⚠️ *അപായ നില*: {risk_str}\n"
            f"📊 *നിലവിലെ ജലനിരപ്പ്*: {water_level_m:.2f}m (അപായ നില: {danger_level_m:.2f}m)\n"
            f"💡 *പ്രധാന കാരണം*: {reason}\n"
            f"🏃 *നിർദ്ദേശിച്ച നടപടി*: {action_str}\n\n"
            f"🗺️ [ഒഴിയൽ പാത മാപ്പ്]({evacuation_url})"
        )
    elif language == "as":
        risk_str = ASSAMESE_RISK_MAP.get(risk_level, risk_level)
        action_str = ASSAMESE_ACTION_MAP.get(risk_level, "সুৰক্ষিত স্থানলৈ যাওক।")
        msg = (
            f"🚨 *বানপানী সকিয়ানী বাৰ্তা*\n\n"
            f"📍 *ষ্টেচন*: {station_name} ({river})\n"
            f"⚠️ *বিপদৰ মাত্ৰা*: {risk_str}\n"
            f"📊 *বৰ্তমান জলস্তৰ*: {water_level_m:.2f}m (বিপদ চিহ্ন: {danger_level_m:.2f}m)\n"
            f"💡 *প্ৰধান কাৰণ*: {reason}\n"
            f"🏃 *প্ৰয়োজনীয় পদক্ষেপ*: {action_str}\n\n"
            f"🗺️ [স্থানান্তৰ পথৰ মানচিত্ৰ]({evacuation_url})"
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
