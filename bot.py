import requests
import json
import time

# =========================================
# BOT CONFIG
# =========================================

BOT_TOKEN = ""  # Paste Bot Token Here

# Dummy HTTPS API Server
EXTERNAL_API_URL = ""  # Example: https://dummyjson.com/users/1

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# =========================================
# SEND MESSAGE
# =========================================

def send_message(chat_id, text, reply_markup=None, parse_mode=None):

    url = f"{BASE_URL}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        requests.post(url, data=payload, timeout=30)

    except Exception as e:
        print("Send Message Error:", e)

# =========================================
# CUSTOM KEYBOARD
# =========================================

def main_keyboard():

    keyboard = {
        "keyboard": [
            [
                {
                    "text": "📱 Phone Lookup"
                }
            ]
        ],
        "resize_keyboard": True
    }

    return keyboard

# =========================================
# PHONE LOOKUP API
# =========================================

def phone_lookup(number):

    try:

        # Example API Call
        response = requests.get(
            EXTERNAL_API_URL,
            timeout=30
        )

        data = response.json()

        result = {
            "searched_number": number,
            "api_response": data
        }

        return json.dumps(result, indent=4)

    except Exception as e:

        error_data = {
            "error": str(e)
        }

        return json.dumps(error_data, indent=4)

# =========================================
# HANDLE USER MESSAGE
# =========================================

def handle_message(message):

    chat_id = message["chat"]["id"]

    if "text" not in message:
        return

    text = message["text"].strip()

    # =====================================
    # START COMMAND
    # =====================================

    if text == "/start":

        welcome_text = (
            "👋 Welcome To Phone Lookup Bot\n\n"
            "Click the button below."
        )

        send_message(
            chat_id,
            welcome_text,
            reply_markup=main_keyboard()
        )

    # =====================================
    # PHONE LOOKUP BUTTON
    # =====================================

    elif text == "📱 Phone Lookup":

        send_message(
            chat_id,
            "📞 Send 10 digit mobile number:"
        )

    # =====================================
    # MOBILE NUMBER CHECK
    # =====================================

    elif text.isdigit() and len(text) == 10:

        send_message(
            chat_id,
            "🔍 Searching..."
        )

        result = phone_lookup(text)

        send_message(
            chat_id,
            f"<pre>{result}</pre>",
            parse_mode="HTML"
        )

    # =====================================
    # INVALID INPUT
    # =====================================

    else:

        send_message(
            chat_id,
            "❌ Invalid Input\n\nSend a valid 10 digit mobile number."
        )

# =========================================
# GET UPDATES
# =========================================

def get_updates(offset=None):

    url = f"{BASE_URL}/getUpdates"

    params = {
        "timeout": 30,
        "offset": offset
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=35
        )

        return response.json()

    except Exception as e:

        print("Get Updates Error:", e)

        return {}

# =========================================
# MAIN BOT LOOP
# =========================================

def run_bot():

    print("Bot Running...")

    offset = None

    while True:

        try:

            updates = get_updates(offset)

            if updates.get("ok"):

                for update in updates["result"]:

                    offset = update["update_id"] + 1

                    if "message" in update:

                        handle_message(update["message"])

            time.sleep(1)

        except Exception as e:

            print("Main Loop Error:", e)

            time.sleep(5)

# =========================================
# START BOT
# =========================================

if __name__ == "__main__":

    run_bot()
