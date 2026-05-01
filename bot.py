import telebot, os, json, time
from telebot.types import ReplyKeyboardMarkup

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7430014980"))

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "data.json"

# ================= DATA =================
def load():
    if not os.path.exists(DATA_FILE):
        return {
            "countries": {},
            "users": {},
            "otp_count": {},
            "channels": [],
            "force_join": False
        }
    return json.load(open(DATA_FILE))

def save():
    json.dump(data, open(DATA_FILE, "w"), indent=2)

data = load()

# ================= API PLACEHOLDER =================
def get_number_from_api():
    return "+8801712345678"

def get_otp_from_api(number):
    return "482913"

# ================= HELPERS =================
def is_admin(uid):
    return uid == ADMIN_ID

def main_menu(uid):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📲 GET NUMBER")
    if is_admin(uid):
        kb.add("⚙ ADMIN PANEL")
    return kb

def save_user(uid):
    data["users"][str(uid)] = True
    if str(uid) not in data["otp_count"]:
        data["otp_count"][str(uid)] = 0
    save()

def check_join(user_id):
    if not data["force_join"]:
        return True
    for ch in data["channels"]:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# ================= START =================
@bot.message_handler(commands=['start'])
def start(msg):
    save_user(msg.chat.id)

    if not check_join(msg.chat.id):
        bot.send_message(msg.chat.id, "❌ Please join required channels first!")
        return

    bot.send_message(msg.chat.id, "✅ Bot Ready", reply_markup=main_menu(msg.chat.id))

# ================= ADMIN PANEL =================
@bot.message_handler(func=lambda m: m.text == "⚙ ADMIN PANEL")
def admin(msg):
    if not is_admin(msg.chat.id): return
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🌍 Add Country", "📞 Add Range")
    kb.add("🤖 Auto Range")
    kb.add("📊 Users", "🔒 Force Join")
    kb.add("➕ Channel", "❌ Channel")
    bot.send_message(msg.chat.id, "⚙ Admin Panel", reply_markup=kb)

# ================= USERS =================
@bot.message_handler(func=lambda m: m.text == "📊 Users")
def users(msg):
    total = len(data["users"])
    txt = f"👥 Total Users: {total}\n\n"

    for uid in list(data["users"])[:10]:
        otp = data["otp_count"].get(uid, 0)
        txt += f"{uid} → OTP: {otp}\n"

    bot.send_message(msg.chat.id, txt)

# ================= COUNTRY =================
@bot.message_handler(func=lambda m: m.text == "🌍 Add Country")
def add_country(msg):
    bot.send_message(msg.chat.id, "Send: +880 Bangladesh")
    bot.register_next_step_handler(msg, save_country)

def save_country(msg):
    code, name = msg.text.split(maxsplit=1)
    data["countries"][name] = {"code": code, "ranges": []}
    save()
    bot.send_message(msg.chat.id, "✅ Country added")

# ================= RANGE =================
@bot.message_handler(func=lambda m: m.text == "📞 Add Range")
def add_range(msg):
    bot.send_message(msg.chat.id, "Send: country start end")
    bot.register_next_step_handler(msg, save_range)

def save_range(msg):
    country, start, end = msg.text.split()
    data["countries"][country]["ranges"].append([start, end])
    save()
    bot.send_message(msg.chat.id, "✅ Range added")

# ================= AUTO RANGE =================
@bot.message_handler(func=lambda m: m.text == "🤖 Auto Range")
def auto_range(msg):
    number = get_number_from_api()
    prefix = number[-11:-8]
    country = "Bangladesh"

    if country not in data["countries"]:
        data["countries"][country] = {"code": "+880", "ranges": []}

    if [prefix, prefix] not in data["countries"][country]["ranges"]:
        data["countries"][country]["ranges"].append([prefix, prefix])
        save()

    bot.send_message(msg.chat.id, f"✅ Auto range added: {prefix}")

# ================= CHANNEL =================
@bot.message_handler(func=lambda m: m.text == "➕ Channel")
def add_channel(msg):
    bot.send_message(msg.chat.id, "Send: @channel")
    bot.register_next_step_handler(msg, save_channel)

def save_channel(msg):
    data["channels"].append(msg.text)
    save()
    bot.send_message(msg.chat.id, "✅ Channel added")

@bot.message_handler(func=lambda m: m.text == "❌ Channel")
def remove_channel(msg):
    bot.send_message(msg.chat.id, "Send: @channel")
    bot.register_next_step_handler(msg, del_channel)

def del_channel(msg):
    if msg.text in data["channels"]:
        data["channels"].remove(msg.text)
        save()
        bot.send_message(msg.chat.id, "✅ Removed")

# ================= FORCE JOIN =================
@bot.message_handler(func=lambda m: m.text == "🔒 Force Join")
def toggle_force(msg):
    data["force_join"] = not data["force_join"]
    save()
    bot.send_message(msg.chat.id, f"Force Join: {data['force_join']}")

# ================= GET NUMBER + OTP =================
@bot.message_handler(func=lambda m: m.text == "📲 GET NUMBER")
def get_number(msg):

    if not check_join(msg.chat.id):
        bot.send_message(msg.chat.id, "❌ Join required channel first!")
        return

    uid = str(msg.chat.id)
    number = get_number_from_api()

    bot.send_message(msg.chat.id, f"📲 Number:\n`{number}`", parse_mode="Markdown")
    bot.send_message(msg.chat.id, "⏳ Waiting for OTP...")

    for i in range(10):
        otp = get_otp_from_api(number)
        if otp:
            data["otp_count"][uid] += 1
            save()

            bot.send_message(msg.chat.id, f"""
✨ <b>Allah always with you, wherever you are</b>

━━━━━━━━━━━━━━━
📲 <b>Number:</b>
<code>{number}</code>

🔐 <b>OTP Code:</b>
<code>{otp}</code>

📊 <b>Total OTP Used:</b> {data["otp_count"][uid]}
━━━━━━━━━━━━━━━

👑 Owner: <b>Ovik</b>
""", parse_mode="HTML")

            return

        time.sleep(3)

    bot.send_message(msg.chat.id, "❌ OTP not received")

bot.remove_webhook()
bot.infinity_polling(skip_pending=True, timeout=10, long_polling_timeout=5)
