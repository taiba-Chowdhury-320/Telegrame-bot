import requests
import json
import time

# =========================================
# BOT CONFIG
# =========================================

BOT_TOKEN = "8980896068:AAEvfqOuIT6JLHWm6t01sWC3ME7fJF-8bJg"

# Dummy HTTPS API
EXTERNAL_API_URL = "https://dummyjson.com/users/1"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# =========================================
# CHANNEL & GROUP
# =========================================

CHANNEL_USERNAME = "@alveeevanroky320"
GROUP_USERNAME = "@alveeevanroky320bot"

CHANNEL_LINK = "https://t.me/alveeevanroky320"
GROUP_LINK = "https://t.me/alveeevanroky320bot"

# =========================================
# VERIFIED USERS MEMORY
# =========================================

verified_users = set()

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
# MAIN KEYBOARD
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
# FORCE JOIN BUTTON
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
            ],
            [
                {
                    "text": "✅ Verify",
                    "callback_data": "verify_join"
                }
            ]
        ]
    }

    return keyboard

# =========================================
# CHECK MEMBERSHIP
# =========================================

def check_membership(user_id):

    try:

        url = f"{BASE_URL}/getChatMember"

        # Check Channel
        channel_params = {
            "chat_id": CHANNEL_USERNAME,
            "user_id": user_id
        }

        channel_response = requests.get(
            url,
            params=channel_params,
            timeout=30
        )

        channel_data = channel_response.json()

        channel_status = channel_data["result"]["status"]

        # Check Group
        group_params = {
            "chat_id": GROUP_USERNAME,
            "user_id": user_id
        }

        group_response = requests.get(
            url,
            params=group_params,
            timeout=30
        )

        group_data = group_response.json()

        group_status = group_data["result"]["status"]

        valid_status = [
            "member",
            "administrator",
            "creator"
        ]

        if channel_status in valid_status and group_status in valid_status:
            return True

        return False

    except Exception as e:

        print("Membership Error:", e)

        return False

# =========================================
# PHONE LOOKUP
# =========================================

def phone_lookup(number):

    try:

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
# CALLBACK ANSWER
# =========================================

def answer_callback(callback_id, text):

    url = f"{BASE_URL}/answerCallbackQuery"

    payload = {
        "callback_query_id": callback_id,
        "text": text
    }

    try:

        requests.post(
            url,
            data=payload,
            timeout=30
        )

    except Exception as e:

        print("Callback Error:", e)

# =========================================
# HANDLE CALLBACK
# =========================================

def handle_callback(callback_query):

    callback_id = callback_query["id"]

    user_id = callback_query["from"]["id"]

    chat_id = callback_query["message"]["chat"]["id"]

    data = callback_query["data"]

    # =====================================
    # VERIFY BUTTON
    # =====================================

    if data == "verify_join":

        joined = check_membership(user_id)

        if joined:

            # Save Verified User
            verified_users.add(user_id)

            answer_callback(
                callback_id,
                "Verification Successful"
            )

            send_message(
                chat_id,
                "✅ Verification Successful\n\nNow You Can Use Bot.",
                reply_markup=main_keyboard()
            )

        else:

            answer_callback(
                callback_id,
                "Join Channel & Group First"
            )

            send_message(
                chat_id,
                "❌ First Join Channel And Group",
                reply_markup=join_keyboard()
            )

# =========================================
# HANDLE MESSAGE
# =========================================

def handle_message(message):

    if "text" not in message:
        return

    chat_id = message["chat"]["id"]

    user_id = message["from"]["id"]

    text = message["text"].strip()

    # =====================================
    # START COMMAND
    # =====================================

    if text == "/start":

        # Already Verified
        if user_id in verified_users:

            send_message(
                chat_id,
                "✅ You Are Already Verified",
                reply_markup=main_keyboard()
            )

            return

        # Check Membership
        joined = check_membership(user_id)

        if joined:

            verified_users.add(user_id)

            send_message(
                chat_id,
                "✅ Verification Successful",
                reply_markup=main_keyboard()
            )

        else:

            send_message(
                chat_id,
                "🚫 Join Channel And Group First",
                reply_markup=join_keyboard()
            )

    # =====================================
    # PHONE LOOKUP BUTTON
    # =====================================

    elif text == "📱 Phone Lookup":

        if user_id not in verified_users:

            send_message(
                chat_id,
                "🚫 First Verify Yourself",
                reply_markup=join_keyboard()
            )

            return

        send_message(
            chat_id,
            "📞 Send 11 digit mobile number:"
        )

    # =====================================
    # 11 DIGIT NUMBER
    # =====================================

    elif text.isdigit() and len(text) == 11:

        if user_id not in verified_users:

            send_message(
                chat_id,
                "🚫 First Verify Yourself",
                reply_markup=join_keyboard()
            )

            return

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
            "❌ Invalid Input\n\nSend Valid 11 Digit Mobile Number."
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
# RUN BOT
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

                    # Handle Message
                    if "message" in update:

                        handle_message(update["message"])

                    # Handle Callback
                    if "callback_query" in update:

                        handle_callback(
                            update["callback_query"]
                        )

            time.sleep(1)

        except Exception as e:

            print("Main Loop Error:", e)

            time.sleep(5)

# =========================================
# START BOT
# =========================================

if __name__ == "__main__":

    run_bot()
