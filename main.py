from tonsdk.contract.wallet import Wallets, WalletVersionEnum
import time
import random
import json
import os
import threading
import telebot
import requests

print("WOMGPT-DGVIKAKA🇻🇳 - TON SUPER FARMER v4.3 (10 VÍ - Chỉ Check All)")

TELEGRAM_TOKEN = "8959793781:AAEPhU8IYadNk5klnUNafWqIsZnH5P8ecp4"
CHAT_ID = "7523022638"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
DATA_FILE = "ton_super_wallets.json"

# ================== TẠO / LOAD 10 VÍ ==================
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        wallets = json.load(f)
    print(f"Đã load {len(wallets)} ví")
else:
    wallets = []
    print("Tạo mới 10 ví V4R2...")
    for i in range(10):
        mnemonics, _, _, wallet = Wallets.create(version=WalletVersionEnum.v4r2, workchain=0)
        address = wallet.address.to_string(True, True, True)
        wallets.append({
            "id": i+1,
            "address": address,
            "mnemonic": " ".join(mnemonics)
        })
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(wallets, f, indent=2, ensure_ascii=False)
    print("✅ Đã tạo 10 ví thành công!")

def check_ton_balance(address):
    try:
        r = requests.get(f"https://tonapi.io/v2/accounts/{address}", timeout=10)
        return round(int(r.json().get('balance', 0)) / 1_000_000_000, 6)
    except:
        return 0.0

def monitor_wallet(wallet):
    while True:
        try:
            bal = check_ton_balance(wallet["address"])
            if bal > 0.001:
                bot.send_message(CHAT_ID, f"💰 **BIG HIT!**\nVí {wallet['id']} có tiền!\nAddress: `{wallet['address']}`\nBalance: **{bal} TON**")
        except:
            pass
        time.sleep(random.randint(600, 1500))

# ===================== TELEGRAM MENU =====================
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(telebot.types.InlineKeyboardButton("🔎 CHECK TẤT CẢ 10 VÍ", callback_data="check_all"))
    markup.add(telebot.types.InlineKeyboardButton("📤 EXPORT ALL MNEMONIC", callback_data="export_mn"))
    
    bot.send_message(CHAT_ID, "🔥 **TON SUPER FARMER v4.3 (10 VÍ)**\nChỉ còn 1 nút Check All như yêu cầu.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    try:
        if call.data == "check_all":
            bot.answer_callback_query(call.id, "Đang check tất cả 10 ví...")
            msg = "📊 **CHECK TẤT CẢ 10 VÍ - CHI TIẾT**\n\n"
            for w in wallets:
                bal = check_ton_balance(w["address"])
                msg += f"**Ví {w['id']}**\nAddress: `{w['address']}`\nBalance: **{bal} TON**\n\n"
            bot.edit_message_text(msg, call.message.chat.id, call.message.message_id)

        elif call.data == "export_mn":
            bot.send_message(CHAT_ID, "⚠️ **MNEMONIC TẤT CẢ 10 VÍ** (Sao chép ngay và xóa tin nhắn):")
            for w in wallets:
                bot.send_message(CHAT_ID, f"Ví {w['id']}: `{w['mnemonic']}`")
    except:
        pass

if __name__ == "__main__":
    bot.send_message(CHAT_ID, "🚀 **TON SUPER FARMER v4.3 ĐÃ ONLINE 24/7!**\nGõ /start để mở menu.")
    
    for wallet in wallets:
        t = threading.Thread(target=monitor_wallet, args=(wallet,), daemon=True)
        t.start()
    
    bot.infinity_polling(none_stop=True)