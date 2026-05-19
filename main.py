from tonsdk.contract.wallet import Wallets, WalletVersionEnum
import time
import random
import json
import os
import threading
import telebot
import requests

print("WOMGPT-DGVIKAKA🇻🇳 - TON MULTI WALLET FARMER v3 (24/7)")

TELEGRAM_TOKEN = "8959793781:AAEPhU8IYadNk5klnUNafWqIsZnH5P8ecp4"
CHAT_ID = "7523022638"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
DATA_FILE = "ton_wallets.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        wallets = json.load(f)
    print(f"Đã load {len(wallets)} ví TON")
else:
    wallets = []
    print("Tạo mới 5 ví TON v4r2...")
    for i in range(5):
        mnemonics, pub_k, priv_k, wallet = Wallets.create(version=WalletVersionEnum.v4r2, workchain=0)
        address = wallet.address.to_string(True, True, True)
        wallets.append({
            "id": i+1,
            "address": address,
            "mnemonic": " ".join(mnemonics)
        })
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(wallets, f, indent=2, ensure_ascii=False)
    print("✅ Đã tạo 5 ví TON mới!")

def check_ton_balance(address):
    try:
        r = requests.get(f"https://tonapi.io/v2/accounts/{address}", timeout=15)
        balance_nano = int(r.json().get('balance', 0))
        return round(balance_nano / 1_000_000_000, 6)
    except:
        return 0.0

def monitor_wallet(wallet):
    while True:
        try:
            bal = check_ton_balance(wallet["address"])
            if bal > 0.001:
                bot.send_message(CHAT_ID, f"💰 **PHÁT HIỆN TIỀN!**\nVí {wallet['id']}\nAddress: `{wallet['address']}`\nBalance: **{bal} TON**")
        except:
            pass
        time.sleep(random.randint(900, 1800))

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    for w in wallets:
        markup.add(telebot.types.InlineKeyboardButton(f"👛 Ví {w['id']} - {w['address'][:8]}...", callback_data=f"check_{w['id']}"))
    markup.add(telebot.types.InlineKeyboardButton("🔎 CHECK TẤT CẢ VÍ", callback_data="check_all"))
    bot.send_message(CHAT_ID, "🔢 **TON WALLET MENU**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        if call.data == "check_all":
            bot.answer_callback_query(call.id, "Đang check...")
            msg = "📊 **CHECK TẤT CẢ VÍ TON**\n\n"
            for w in wallets:
                bal = check_ton_balance(w["address"])
                msg += f"Ví {w['id']}: `{w['address'][:8]}...` → **{bal} TON**\n"
            bot.edit_message_text(msg, call.message.chat.id, call.message.message_id)
        elif call.data.startswith("check_"):
            vid = int(call.data.split("_")[1])
            wallet = next((w for w in wallets if w["id"] == vid), None)
            if wallet:
                bal = check_ton_balance(wallet["address"])
                bot.send_message(CHAT_ID, f"📌 **Ví {vid}**\nAddress: `{wallet['address']}`\nBalance: **{bal} TON**")
    except:
        pass

if __name__ == "__main__":
    bot.send_message(CHAT_ID, "🚀 **TON FARMER 24/7 ĐÃ ONLINE!**\nGõ /start để dùng.")
    for wallet in wallets:
        threading.Thread(target=monitor_wallet, args=(wallet,), daemon=True).start()
    bot.infinity_polling(none_stop=True)