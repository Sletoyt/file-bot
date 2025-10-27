import os
import telegram
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask, request

BOT_TOKEN = "8347361707:AAHGPqpYoSqfKeex_QSvb6Wgg-BjeXD7Q10"
ADMIN_ID = 7843231115  # आपका admin user id
CHANNEL_ID = -1002714387561  # file storage channel id

app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

# Admin द्वारा फाइल भेजें
async def upload(update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("सिर्फ एडमिन अपलोड कर सकता है!")
        return

    # file को चैनल पर forward करें
    if update.message.document:
        file_id = update.message.document.file_id
        # चैनल में फॉरवर्ड करें
        channel_msg = await context.bot.forward_message(chat_id=CHANNEL_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
        message_id = channel_msg.message_id
        # unique deep link बनाएं
        deep_link = f"https://t.me/adultvideofree_bot?start=file_{message_id}"
        await update.message.reply_text(f"Deep link ready:\n{deep_link}")

upload_handler = CommandHandler("upload", upload)
application.add_handler(upload_handler)

# Deep link से फाइल भेजें
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args and args[0].startswith("file_"):
        message_id = int(args[0].replace("file_", ""))
        # चैनल से फाइल ले कर भेजें
        await context.bot.copy_message(chat_id=update.effective_chat.id, from_chat_id=CHANNEL_ID, message_id=message_id)
    else:
        await update.message.reply_text("Welcome! Send /upload to upload a file (admin only)")

application.add_handler(CommandHandler("start", start))

# Flask server for keep_alive
@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Bot and server को संगीत रखें
import threading
def run_bot():
    application.run_polling()

t1 = threading.Thread(target=run_bot)
t2 = threading.Thread(target=run_flask)
t1.start()
t2.start()
