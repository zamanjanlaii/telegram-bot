import time
import telebot
from telebot import types
import json
from datetime import datetime

# 🛡️ Telegram Bot Token
TOKEN = "7688164243:AAGg5-FmFW3FzEGBT-txW5CRQc6GRPC11ns"
bot = telebot.TeleBot(TOKEN)

# 📌 Bot Sahibinin Kullanıcı ID'si
OWNER_ID = 7423350654

# 📌 Kanalların ID'leri ve Linkleri
CHANNELS = {
    "-1002308678665": "https://t.me/Zamana_Servers",       # ✅  Kontrol Edilecek
    "-1002664527497": "https://t.me/crayzy41",  # ✅  Kontrol Edilecek
    "-1002434323427": "https://t.me/BEGA_VPNS1",           # ✅  Kontrol Edilecek
}

# 🚫 Bu kanal kontrol edilmeyecek, sadece butonu gösterilecek
EXCLUDED_CHANNEL_LINK = "https://t.me/SERVERSTM"

# 📊 Kullanıcı Verilerini Saklayan Dosya
USER_DATA_FILE = "users.json"

# 📌 Kullanıcı verilerini yükle
def load_user_data():
    try:
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# 📌 Kullanıcı verilerini kaydet
def save_user_data(data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# 📂 Kullanıcıları takip eden sözlük
users = load_user_data()

# 🎯 **/start Komutu**
@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.chat.id)
    today = datetime.now().strftime("%Y-%m-%d")
    if user_id not in users:
        users[user_id] = {"checked": False, "joined_at": today}
        save_user_data(users)
    bot.send_message(
        message.chat.id,
        f"👋 𝐒𝐚𝐥𝐚𝐦, {message.from_user.first_name} 👋\n\n"
        "𝐀𝐬𝐚𝐠𝐢𝐝𝐚𝐤𝐢 𝐤𝐚𝐧𝐚𝐥𝐥𝐚𝐫𝐚 𝐚𝐠𝐳𝐚 𝐛𝐨𝐥𝐮𝐩, 𝐕𝐈𝐏 𝐕𝐏𝐍 𝐤𝐨𝐝𝐮𝐧𝐮 𝐚𝐥𝐚𝐛𝐢𝐥𝐢𝐫𝐬𝐢𝐧𝐢𝐳 ✅ ",
        reply_markup=start_markup(),
        parse_mode="Markdown"
    )

# ✅  **"Agza Boldum" Butonu Basıldığında Kontrol Etme**
@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_subscription(call):
    user_id = str(call.from_user.id)
    missing_channels = []
    for channel_id, channel_link in CHANNELS.items():
        try:
            member = bot.get_chat_member(channel_id, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                missing_channels.append((channel_id, channel_link))
        except telebot.apihelper.ApiException as e:
            print(f"⚠️ Hata: {e} Kanal ID: {channel_id}")
            missing_channels.append((channel_id, channel_link))
    if not missing_channels:
        vpn_code = "ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTptcHMzRndtRGpMcldhT1Zn@74.177.114.146:443"
        bot.send_message(call.message.chat.id, f"✅  Tebrikler! Kanallara üye oldunuz.\n\n🔑 VPN Kodunuz:\n`{vpn_code}`", parse_mode="Markdown")
        shadowwocks_message = "🌟 **𝑩𝑬𝑳𝑬𝑻 𝑯𝒀𝑺𝑴𝑨𝑻𝒀𝑵𝑫𝑨𝑵 𝑷𝑬𝑌𝑫𝑨𝑳𝑨𝑵 🥂!** 🌟\n\n" \
                              "Bellet-Film💠\n\n" \
                              "1⃣-AÝLYK ✔️\n\n" \
                              "1⃣-ADAMLYK 💼\n\n" \
                              "BAHASY: 15TMT📶\n\n" \
                              "📣Habarlasmak: [@Zamanlai_06_07](https://t.me/Zamanlai_06_07) 📌 " \
                              "Halal , Halal , Halal ."
        bot.send_message(call.message.chat.id, shadowwocks_message, parse_mode="Markdown")
        if user_id in users:
            users[user_id]["checked"] = True
            save_user_data(users)
    else:
        markup = types.InlineKeyboardMarkup()
        msg = "🚨 *Tüm kanallara üye olmamışsınız!* Aşağıdaki kanallara katılın: \n\n"
        for channel_id, channel_link in missing_channels:
            button = types.InlineKeyboardButton(text="📢 Kanal", url=channel_link)
            markup.add(button)
            msg += f"🔹 [Kanal Linki]({channel_link})\n"
        check_button = types.InlineKeyboardButton(text="✅  𝑨𝒈𝑧𝒂 𝑩𝒐𝒍𝒅𝒖𝒎 ✅ ", callback_data="check")
        markup.add(check_button)
        bot.send_message(call.message.chat.id, msg, reply_markup=markup, parse_mode="Markdown")

# 📌 **/adam Komutu Eklendi**
@bot.message_handler(commands=["adam"])
def adam(message):
    if message.chat.id == OWNER_ID:
        total_users = len(users)
        total_members = sum(1 for user in users.values() if user["checked"])
        missing_members = total_users - total_members
        today = datetime.now().strftime("%Y-%m-%d")
        new_users_today = sum(1 for user in users.values() if user["joined_at"] == today)
        members_today = sum(1 for user in users.values() if user["checked"] and user["joined_at"] == today)
        
        # Büyüme oranı hesaplama
        if total_users > 1:
            growth_rate = ((total_members / total_users) * 100)
        else:
            growth_rate = 0.0
        
        # Raporu oluştur
        report = f"""
        📊 Bot Üye Raporu:
        👥 Toplam Kullanıcı: {total_users}
        ✅ Tam Üye Olanlar: {total_members}
        ❌ Eksik Üyeliği Olanlar: {missing_members}
        📈 Günlük Yeni Kullanıcılar: {new_users_today}
        🟢 Bugün Tam Üye Olanlar: {members_today}
        📊 Büyüme Oranı: %{growth_rate:.2f}
        """
        bot.send_message(message.chat.id, report, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Bu komutu kullanma yetkiniz yok!")

# 🚀 **start_markup Fonksiyonu**
def start_markup():
    markup = types.InlineKeyboardMarkup()
    # Kanal 1 ve Kanal 2 aynı satırda
    row1 = [
        types.InlineKeyboardButton(text="⚡  𝑲𝒂𝒏𝒂𝒍 ⚡ ", url=CHANNELS["-1002308678665"]),
        types.InlineKeyboardButton(text="🔐 𝑲𝒂𝒏𝒂𝒍  🔐", url=CHANNELS["-1002664527497"])
    ]
    markup.row(*row1)
    # Kanal 3 aynı satırda, EXCLUDED_CHANNEL sadece buton olarak var
    row2 = [
        types.InlineKeyboardButton(text="🔥 𝑲𝒂𝒏𝒂𝒍 🔥", url=CHANNELS["-1002434323427"]),
        types.InlineKeyboardButton(text="🌶️ 𝑺𝑬𝑹𝑾𝑬𝑹𝑺 𝑻𝑴 🌶️", url=EXCLUDED_CHANNEL_LINK)  # ❌M Test Edilmeyen Kanal
    ]
    markup.row(*row2)
    # "Dosya Ekle" butonu en altta
    file_button = types.InlineKeyboardButton(text="📂 𝑼𝑳𝑻𝑹𝑨 𝑽𝑷𝑵 (𝑯𝑶𝑲𝑴𝑨𝑵 𝑨𝑮𝑩𝑶𝑳 𝑩𝑶𝑳)", url="https://t.me/addlist/9Jr1GsqqE0JkZTIy")
    markup.add(file_button)
    # "Agza Boldum" butonu en altta
    agza_button = types.InlineKeyboardButton(text="✅  𝑨𝒈𝑧𝒂 𝑩𝒐𝒍𝒅𝒖𝒎 ✅ ", callback_data="check")
    markup.add(agza_button)
    return markup

# 🚀 **Termux çalıştırma kısmı**
@bot.message_handler(commands=["run"])
def run(message):
    bot.send_message(message.chat.id, "Bot başlatılıyor...")

if __name__ == "__main__":
    print("📡 Bot başlatılıyor...")
    while True:
        try:
            bot.polling(none_stop=True, interval=3, timeout=60)
        except Exception as e:
            print(f"⚠️ Hata: {e}")
            time.sleep(5)