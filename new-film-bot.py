from flask import Flask
import threading
import telebot

# Flask app
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "salom bot ishlayapti", 200

# Telegram token va sozlamalar
TOKEN = "7731979739:AAEAX1_tO4651WGNuinVrj1QZGKe-nQg6tk"
bot = telebot.TeleBot(TOKEN)

# Konfiguratsiya
admin = "7445956027"
baza_channel_id = "-3183257356"
kanal_username = "turon_film"

# Yordamchi funksiyalar
def get_chat_member_status(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status
    except Exception:
        return None

def join_chat(user_id):
    kanallar = "@Uzvakilov"
    if not kanallar:
        return True

    uns = False
    inline_keyboard = []
    for kanal in kanallar.split("\n"):
        kanal = kanal.strip()
        if not kanal:
            continue
        url = kanal.lstrip('@')
        try:
            chat = bot.get_chat(f"@{url}")
            chat_title = chat.title or url
        except Exception:
            chat_title = url

        status = get_chat_member_status(f"@{url}", user_id)

        if status in ["creator", "administrator", "member"]:
            inline_keyboard.append([{"text": f"✅ {chat_title}", "url": f"https://t.me/{url}"}])
        else:
            inline_keyboard.append([{"text": f"❌ {chat_title}", "url": f"https://t.me/{url}"}])
            uns = True

    inline_keyboard.append([{"text": "🔄 Tekshirish", "url": "https://t.me/your_bot_username?start"}])

    if uns:
        bot.send_message(user_id, "⚠️ Botdan to'liq foydalanish uchun quyidagi kanallarimizga obuna bo'ling!", reply_markup={"inline_keyboard": inline_keyboard})
        return False
    return True

# Handlerlar
@bot.message_handler(commands=['start'])
def handle_start_command(message):
    chat_id = message.chat.id
    if join_chat(chat_id):
        bot.send_video(
            chat_id, 
            f"https://t.me/{kanal_username}/170", 
            caption="👑 Assalomu alaykum. Kino kodini kiriting:", 
            reply_markup={"inline_keyboard":[[{"text":"🎦 KINOLARNI TOPISH","url":f"https://t.me/{kanal_username}"}]]}
        )

@bot.message_handler(content_types=['video'])
def handle_video_message(message):
    chat_id = message.chat.id
    message_id = message.message_id
    try:
        result = bot.copy_message(chat_id=baza_channel_id, from_chat_id=chat_id, message_id=message_id)
        new_message_id = None
        if hasattr(result, 'message_id'):
            new_message_id = result.message_id
        else:
            try:
                new_message_id = result.get('message_id')
            except Exception:
                new_message_id = None

        if new_message_id:
            bot.send_message(
                chat_id, 
                f"🚀 Botga yangi kino yuklandi!\n#️⃣ Film kodi: {new_message_id}", 
                reply_markup={"inline_keyboard":[[{"text":"Postni koʻrish","url":f"https://t.me/{kanal_username}/{new_message_id}"}]]}
            )
            with open("last.txt", "w") as f:
                f.write(str(new_message_id))
        else:
            bot.send_message(chat_id, "Xatolik: postni ko'chirib bo'lmadi.")
    except Exception as e:
        bot.send_message(chat_id, f"Xatolik yuz berdi: {e}")

# Botni alohida threadda ishga tushirish
def run_bot_polling():
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

if __name__ == "__main__":
    # Polling threadni ishga tushiramiz
    t = threading.Thread(target=run_bot_polling)
    t.daemon = True
    t.start()

    # Flask serverni ishga tushuramiz
    app.run(host="0.0.0.0", port=5000, debug=True)
