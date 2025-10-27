import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import base64

TOKEN = "8347361707:AAHGPqpYoSqfKeex_QSvb6Wgg-BjeXD7Q10"
ADMIN_ID = 7843231115
CHANNEL_ID = -1002714387561

# फाइलों की deep link जानकारी
deep_files = {}  # {'deepid': 'filepath'}

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    Thread(target=run).start()

keep_alive()

# एडमिन के द्वारा फाइल भेजना
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ADMIN_ID and update.message.document:
        file = await context.bot.get_file(update.message.document.file_id)
        filename = update.message.document.file_name
        filepath = f"files/{filename}"
        os.makedirs("files", exist_ok=True)
        await file.download_to_drive(filepath)
        deepid = base64.urlsafe_b64encode(filename.encode()).decode()
        deep_files[deepid] = filepath
        # चैनल पर भेज दें फाइल
        await context.bot.send_document(CHANNEL_ID, open(filepath, "rb"), caption=f"Uploaded by admin")
        # deep link बनाएं
        deep_link = f"https://t.me/adultvideofree_bot?start={deepid}"
        await update.message.reply_text(f"फाइल की Deep Link:\n{deep_link}")
    elif update.message.document:
        await update.message.reply_text("सिर्फ एडमिन को deep link मिल सकती है।")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        deepid = args[0]
        if deepid in deep_files:
            filepath = deep_files[deepid]
            await update.message.reply_document(open(filepath, "rb"))
        else:
            await update.message.reply_text("फाइल उपलब्ध नहीं है या लिंक गलत है।")
    else:
        await update.message.reply_text("Bot is Active।")

app_telegram = Application.builder().token(TOKEN).build()
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(MessageHandler(filters.Document.ALL, handle_document))

app_telegram.run_polling()
                          
