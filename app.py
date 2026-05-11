from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# ============================================================
#  PASTE YOUR CREDENTIALS HERE (from Meta Developer Dashboard)
# ============================================================
PHONE_NUMBER_ID = "1174001225778019"
ACCESS_TOKEN    = "EAATbIWLTlk4BRXbrNLX49nB4b9KYyduY8xTBejWqbu69LtuZBM4nE8Y7pQhKow62wjTa2BWR8Ff9SqF7o8J1ET6SxVXceIfxDric2o34DskHkADsgLHllUvx5P2B3zYZCrYlHSsKqZAEJmOQsOhk3kY5K1YrJWRT4NEQmy8jrz07zCV0ZC9ntZCkm7PqTZAuJ3y9tMhhRWqQ0YKhGGnHD7ESbew2ZCix19FkU0tMUVVbUl4ZCkgyBFeCWkujgHsqyaSv3nxc3ZCt0sQbXC61XsKpI"
VERIFY_TOKEN    = "mybookbot"          # You can change this word
# ============================================================

API_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# ============================================================
#  YOUR BOOK CATALOGUE — Edit with your real books & prices
# ============================================================
BOOKS = {
    "1": {"title": "African History Vol. 1",     "price": "KES 850",  "genre": "History"},
    "2": {"title": "Business Startup Guide",      "price": "KES 1200", "genre": "Business"},
    "3": {"title": "Swahili Poetry Collection",   "price": "KES 650",  "genre": "Poetry"},
    "4": {"title": "Kenya Primary Science Bk 4",  "price": "KES 450",  "genre": "Education"},
    "5": {"title": "Nairobi Nights (Novel)",       "price": "KES 750",  "genre": "Fiction"},
}

# Track conversation state per customer
user_sessions = {}

# ============================================================
#  WEBHOOK VERIFICATION (Meta requires this step)
# ============================================================
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode      = request.args.get("hub.mode")
    token     = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verified!")
        return challenge, 200  # <--- THIS MUST BE THE CHALLENGE STRING
    return "Forbidden", 403


# ============================================================
#  RECEIVE MESSAGES
# ============================================================
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()

    try:
        message_data = data["entry"][0]["changes"][0]["value"]

        # Ignore delivery receipts / status updates
        if "messages" not in message_data:
            return jsonify({"status": "ok"}), 200

        message  = message_data["messages"][0]
        customer = message["from"]           # Customer's WhatsApp number
        msg_type = message["type"]

        # Get text from message
        if msg_type == "text":
            text = message["text"]["body"].strip()
        elif msg_type == "interactive":
            text = message["interactive"]["button_reply"]["id"]
        else:
            text = ""

        print(f"📩 Message from {customer}: {text}")

        # Process and reply
        handle_message(customer, text)

    except Exception as e:
        print(f"❌ Error: {e}")

    return jsonify({"status": "ok"}), 200


# ============================================================
#  BOT LOGIC — Conversation Flow
# ============================================================
def handle_message(customer, text):
    text_lower = text.lower().strip()

    # Greetings trigger main menu
    greetings = ["hi", "hello", "hey", "hujambo", "habari", "start", "menu", "0"]
    if text_lower in greetings or customer not in user_sessions:
        user_sessions[customer] = {"state": "main_menu"}
        send_main_menu(customer)
        return

    state = user_sessions.get(customer, {}).get("state", "main_menu")

    # ── Main Menu selections ──────────────────────────────
    if state == "main_menu":

        if text == "1":
            send_catalogue(customer)
            user_sessions[customer]["state"] = "browsing"

        elif text == "2":
            send_text(customer,
                "📦 *Check Your Order Status*\n\nPlease type your Order Number (e.g. ORD-001):")
            user_sessions[customer]["state"] = "check_order"

        elif text == "3":
            send_delivery_info(customer)

        elif text == "4":
            send_text(customer,
                "🏫 *Bulk / School Orders*\n\n"
                "Please send us the following details:\n\n"
                "1️⃣ School / Institution Name\n"
                "2️⃣ Contact Person & Phone\n"
                "3️⃣ List of books needed & quantities\n\n"
                "Our team will send a quote within 2 hours. ✅")
            user_sessions[customer]["state"] = "bulk_order"

        elif text == "5":
            send_text(customer,
                "📞 *Talk to Our Team*\n\n"
                "Our customer care team will respond shortly.\n\n"
                "🕐 Working Hours: Mon–Sat, 8am–6pm\n"
                "📧 Email: support@yourbookstore.co.ke\n\n"
                "Type *menu* to go back to the main menu.")

        else:
            send_text(customer, "❓ Please choose an option from 1 to 5, or type *menu* to start over.")

    # ── Browsing catalogue — customer picks a book ────────
    elif state == "browsing":
        if text in BOOKS:
            book = BOOKS[text]
            send_text(customer,
                f"📖 *{book['title']}*\n"
                f"💰 Price: {book['price']}\n"
                f"📚 Genre: {book['genre']}\n\n"
                f"To order, reply *ORDER {text}*\n"
                f"Or type *menu* to go back.")
        elif text_lower.startswith("order "):
            book_id = text.split(" ")[-1]
            if book_id in BOOKS:
                book = BOOKS[book_id]
                send_text(customer,
                    f"✅ *Order Confirmed!*\n\n"
                    f"📖 {book['title']}\n"
                    f"💰 {book['price']}\n\n"
                    f"*Payment Instructions:*\n"
                    f"Go to M-Pesa → Lipa Na M-Pesa → Pay Bill\n"
                    f"Business No: 123456\n"
                    f"Account No: Your WhatsApp number\n\n"
                    f"After payment, send us your M-Pesa confirmation code and we will process your order. 🚀")
                user_sessions[customer]["state"] = "awaiting_payment"
            else:
                send_text(customer, "❌ Book not found. Type *menu* to see our catalogue.")
        else:
            send_text(customer, "Type the book number (1-5) to see details, or type *menu* to go back.")

    # ── Order status check ────────────────────────────────
    elif state == "check_order":
        send_text(customer,
            f"🔍 Checking order *{text}*...\n\n"
            f"📦 Status: *In Processing*\n"
            f"🚚 Estimated delivery: 1-2 business days (Nairobi)\n\n"
            f"For more help, type *5* to talk to our team.\n"
            f"Type *menu* to go back.")
        user_sessions[customer]["state"] = "main_menu"

    # ── Awaiting M-Pesa payment confirmation ──────────────
    elif state == "awaiting_payment":
        if len(text) >= 8:   # M-Pesa codes are typically 10 chars
            send_text(customer,
                f"🎉 *Thank you!*\n\n"
                f"We have received your payment code: *{text}*\n"
                f"Our team will verify and dispatch your order within 2 hours.\n\n"
                f"You will receive a delivery notification here on WhatsApp. 📦\n\n"
                f"Type *menu* to go back to main menu.")
            user_sessions[customer]["state"] = "main_menu"
        else:
            send_text(customer,
                "Please send a valid M-Pesa confirmation code (e.g. *RGK7X12345*)")

    # ── Bulk order — collect details ──────────────────────
    elif state == "bulk_order":
        send_text(customer,
            f"✅ *Bulk Order Request Received!*\n\n"
            f"Thank you! Our sales team will contact you within 2 hours with a quote.\n\n"
            f"Type *menu* to go back to main menu.")
        user_sessions[customer]["state"] = "main_menu"

    else:
        send_main_menu(customer)


# ============================================================
#  MESSAGE SENDERS
# ============================================================
def send_main_menu(customer):
    send_text(customer,
        "📚 *Welcome to Our Bookstore!*\n\n"
        "How can we help you today?\n\n"
        "1️⃣  Browse Book Catalogue\n"
        "2️⃣  Check Order Status\n"
        "3️⃣  Delivery & Shipping Info\n"
        "4️⃣  Bulk / School Orders\n"
        "5️⃣  Talk to Our Team\n\n"
        "Reply with a number (1-5) 👇")


def send_catalogue(customer):
    catalogue = "📖 *Our Book Catalogue*\n\n"
    for num, book in BOOKS.items():
        catalogue += f"{num}️⃣  *{book['title']}*\n    💰 {book['price']} | {book['genre']}\n\n"
    catalogue += "Reply with a number to see details & order.\nType *menu* to go back."
    send_text(customer, catalogue)


def send_delivery_info(customer):
    send_text(customer,
        "🚚 *Delivery & Shipping Info*\n\n"
        "📍 *Nairobi CBD & Estates:* 1–2 business days — KES 200\n"
        "📍 *Other Kenyan Towns:* 3–5 business days — KES 350\n"
        "📍 *Free Delivery* on orders above KES 3,000\n\n"
        "📦 We use G4S, Wells Fargo & local courier partners.\n\n"
        "Type *menu* to go back to main menu.")


def send_text(customer, message):
    payload = {
        "messaging_product": "whatsapp",
        "to": customer,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    print(f"📤 Sent to {customer}: {response.status_code}")
    return response


# ============================================================
#  RUN THE APP
# ============================================================
if __name__ == "__main__":
    app.run(port=5000, debug=True)
