from tonsdk.contract.wallet import Wallets, WalletVersionEnum
import time
import random
import json
import os
import threading
import telebot
import requests
from datetime import datetime

print("WOMGPT-DGVIKAKA🇻🇳 - TON SUPER FARMER v4 (Mạnh Nhất - No Capital)")

TELEGRAM_TOKEN = "8959793781:AAEPhU8IYadNk5klnUNafWqIsZnH5P8ecp4"
CHAT_ID = "7523022638"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
DATA_FILE = "ton_super_wallets.json"
JETTONS = ["EQ..."]  # Có thể thêm contract jetton sau

# ================== TẠO / LOAD VÍ ==================
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        wallets = json.load(f)
    print(f"Đã load {len(wallets)} ví farm mạnh")
else:
    wallets = []
    print("Tạo 10 ví V4R2 mạnh nhất...")
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
    print("✅ Tạo 10 ví farm thành công!")

def check_ton_balance(address):
    try:
        r = requests.get(f"https://tonapi.io/v2/accounts/{address}", timeout=10)
        return round(int(r.json().get('balance', 0)) / 1_000_000_000, 6)
    except:
        return 0.0

def check_jetton_balance(address, jetton_master):
    try:
        r = requests.get(f"https://tonapi.io/v2/accounts/{address}/jettons", timeout=10)
        for j in r.json().get('balances', []):
            if j['jetton']['address'] == jetton_master:
                return float(j['balance']) / (10 ** j['jetton']['decimals'])
    except:
        pass
    return 0.0

def monitor_wallet(wallet):
    while True:
        try:
            ton = check_ton_balance(wallet["address"])
            msg = f"🔥 **Ví {wallet['id']}**\nAddress: `{wallet['address']}`\nTON: **{ton}**\n"
            
            if ton > 0.001:
                bot.send_message(CHAT_ID, f"💰 **BIG HIT!** Ví {wallet['id']} có {ton} TON!")
            
            time.sleep(random.randint(600, 1200))
        except:
            time.sleep(30)

# ===================== TELEGRAM MENU =====================
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    for w in wallets:
        markup.add(telebot.types.InlineKeyboardButton(f"👛 Ví {w['id']}", callback_data=f"check_{w['id']}"))
    markup.add(telebot.types.InlineKeyboardButton("🔎 CHECK ALL", callback_data="check_all"))
    markup.add(telebot.types.InlineKeyboardButton("📤 EXPORT MNEMONIC", callback_data="export_mn"))
    bot.send_message(CHAT_ID, "🚀 **TON SUPER FARMER v4 ONLINE**\n10 ví đang farm mạnh!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    try:
        if call.data == "check_all":
            msg = "📊 **CHECK ALL WALLETS**\n\n"
            for w in wallets:
                ton = check_ton_balance(w["address"])
                msg += f"Ví {w['id']}: `{w['address'][:8]}...` → **{ton} TON**\n"
            bot.edit_message_text(msg, call.message.chat.id, call.message.message_id)

        elif call.data.startswith("check_"):
            vid = int(call.data.split("_")[1])
            wallet = next((w for w in wallets if w["id"] == vid), None)
            if wallet:
                ton = check_ton_balance(wallet["address"])
                bot.send_message(CHAT_ID, f"📌 **Ví {vid}**\n`{wallet['address']}`\nTON: **{ton}**")

        elif call.data == "export_mn":
            bot.send_message(CHAT_ID, "⚠️ **MNEMONIC TẤT CẢ VÍ** (Lưu ngay rồi xóa tin nhắn):")
            for w in wallets:
                bot.send_message(CHAT_ID, f"Ví {w['id']}: `{w['mnemonic']}`")
    except:
        pass

if __name__ == "__main__":
    bot.send_message(CHAT_ID, "🔥 **TON SUPER FARMER v4 ĐÃ KHỞI ĐỘNG 24/7!**\n10 ví đang chạy mạnh.\nGõ /start")
    
    for wallet in wallets:
        threading.Thread(target=monitor_wallet, args=(wallet,), daemon=True).start()
    
    bot.infinity_polling(none_stop=True)