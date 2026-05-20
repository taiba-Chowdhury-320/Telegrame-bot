import requests
import json
import time
import threading
import os

from http.server import BaseHTTPRequestHandler, HTTPServer


# =========================================
# BOT SETTINGS
# =========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

API_URL = "https://dummyjson.com/users/1"

CHANNEL_USERNAME = "@alveeevanroky320"

GROUP_USERNAME = "@alveeevanroky320bot"

CHANNEL_LINK = "https://t.me/alveeevanroky320"

GROUP_LINK = "https://t.me/alveeevanroky320bot"


BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================================
# SEND MESSAGE
# =========================================

def send_message(chat_id, text, reply_markup=None):

    url = f"{BASE_URL}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    requests.post(url, data=data)


# =========================================
# CHECK USER JOINED OR NOT
# =========================================

def check_membership(user_id):

    try:

        url = f"{BASE_URL}/getChatMember"

        channel_data = {
            "chat_id": CHANNEL_USERNAME,
            "user_id": user_id
        }

        group_data = {
            "chat_id": GROUP_USERNAME,
            "user_id": user_id
        }

        channel_response = requests.post(url, data=channel_data).json()

        group_response = requests.post(url, data=group_data).json()

        channel_status = channel_response["result"]["status"]

        group_status = group_response["result"]["status"]

        allowed = ["member", "administrator", "creator"]

        if channel_status in allowed and group_status in allowed:
            return True

        return False

    except Exception as e:

        print("Membership Error:", e)

        return False


# =========================================
# JOIN BUTTONS
# =========================================

def join_keyboard():

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "📢 Join Channel",
                    "url": CHANNEL_LINK
                }
            ],
            [
                {
                    "text": "👥 Join Group",
                    "url": GROUP_LINK
                }
            ]
        ]
    }

    return keyboard


# =========================================
# MAIN MENU
# =========================================

def main_menu():

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
# GET UPDATES
# =========================================

def get_updates(offset):

    url = f"{BASE_URL}/getUpdates"

    params = {
        "timeout": 30,
        "offset": offset
    }

    response = requests.get(url, params=params)

    return response.json()


# =========================================
# PHONE LOOKUP
# =========================================

def phone_lookup(number):

    try:

        response = requests.get(API_URL)

        data = response.json()

        pretty = json.dumps(data, indent=4)

        return pretty

    except Exception as e:

        return str(e)


# =========================================
# DUMMY WEB SERVER
# =========================================

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)

        self.send_header("Content-type", "text/html")

        self.end_headers()

        self.wfile.write(b"Bot Running")


def run_web():

    port = int(os.environ.get("PORT", 10000))

    server = HTTPServer(("0.0.0.0", port), Handler)

    server.serve_forever()


# =========================================
# BOT LOOP
# =========================================

def run_bot():

    print("Bot Running...")

    offset = 0

    while True:

        try:

            updates = get_updates(offset)

            if "result" in updates:

                for update in updates["result"]:

                    offset = update["update_id"] + 1

                    if "message" not in update:
                        continue

                    message = update["message"]

                    chat_id = message["chat"]["id"]

                    user_id = message["from"]["id"]

                    text = message.get("text", "")

                    # ==========================
                    # START COMMAND
                    # ==========================

                    if text == "/start":

                        joined = check_membership(user_id)

                        if joined:

                            send_message(
                                chat_id,
                                "✅ Verified Successfully\n\nWelcome To Phone Lookup Bot",
                                main_menu()
                            )

                        else:

                            send_message(
                                chat_id,
                                "⚠️ Join Channel And Group First",
                                join_keyboard()
                            )

                    # ==========================
                    # PHONE LOOKUP BUTTON
                    # ==========================

                    elif text == "📱 Phone Lookup":

                        joined = check_membership(user_id)

                        if joined:

                            send_message(
                                chat_id,
                                "📞 Send 11 digit Bangladesh mobile number:"
                            )

                        else:

                            send_message(
                                chat_id,
                                "❌ Join Channel And Group First",
                                join_keyboard()
                            )

                    # ==========================
                    # PHONE NUMBER CHECK
                    # ==========================

                    elif text.isdigit():

                        joined = check_membership(user_id)

                        if not joined:

                            send_message(
                                chat_id,
                                "❌ Join Channel And Group First",
                                join_keyboard()
                            )

                            continue

                        if len(text) == 11:

                            result = phone_lookup(text)

                            send_message(
                                chat_id,
                                f"<pre>{result}</pre>"
                            )

                        else:

                            send_message(
                                chat_id,
                                "❌ Invalid Number\n\nSend valid 11 digit Bangladesh number."
                            )

        except Exception as e:

            print("Error:", e)

            time.sleep(5)


# =========================================
# START BOT
# =========================================

if __name__ == "__main__":

    t1 = threading.Thread(target=run_web)

    t1.start()

    run_bot()
