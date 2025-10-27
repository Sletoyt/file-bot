import os
from flask import Flask
from threading import Thread
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes
import base64

# Bot credentials
TOKEN = "8347361707:AAHGPqpYoSqfKeex_QSvb6Wgg-BjeXD7Q10"
ADMIN_ID = 7843231115
CHANNEL_ID = -1002714387561

# फाइलों की deep link जानकारी
deep_files = {}  # {'deepid': 'filepath'}

# Flask for keep_alive (Replit)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    Thread(target=run).start()

keep_alive()

# फाइल एडमिन द्वारा अपलोड करने का /upload command
async def upload_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("सिर्फ एडमिन ही फाइल अपलोड कर सकता है।")
        return
    if not update.message.document:
        await update.message.reply_text("कृपया कोई फाइल भेजें।")
        return
    # फाइल सेव करें
    file = await context.bot.get_file(update.message.document.file_id)
    filename = update.message.document.file_name
    filepath = f"files/{filename}"
    os.makedirs("files", exist_ok=True)
    await file.download_to_drive(filepath)
    # deep link जनरेट करें
    deepid = base64.urlsafe_b64encode(filename.encode()).decode()
    deep_files[deepid] = filepath
    # फाइल को चैनल में भेजें
    await context.bot.send_document(CHANNEL_ID, open(filepath, "rb"), caption=f"Uploaded by admin")
    deep_link = f"https://t.me/adultvideofree_bot?start={deepid}"
    await update.message.reply_text(f"Deep Link:\n{deep_link}")

# deep link से start par फाइल भेजना
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        deepid = args[0]
        if deepid in deep_files:
            filepath = deep_files[deepid]
            await update.message.reply_document(open(filepath, "rb"))
        else:
            await update.message.reply_text("फाइल मिल नहीं रही है। संभवतः लिंक एक्सपायर/गलत है।")
    else:
        await update.message.reply_text("बोट एक्टिव है!")

app_telegram = Application.builder().token(TOKEN).build()
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("upload", upload_file))
app_telegram.run_polling()
            
