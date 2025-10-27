import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, jsonify
from threading import Thread

API_ID = 16267139
API_HASH = "e0bdab938a5b5d771411f45ee12a9f2b"
BOT_TOKEN = "8347361707:AAHGPqpYoSqfKeex_QSvb6Wgg-BjeXD7Q10"
ADMIN_ID = 7843231115
CHANNEL_ID = -1002714387561 
BOT_USERNAME = "adultvideofree_bot"
CHANNEL_LINK = "https://t.me/+fnk2mum5ClNhMWM9"

app = Client(
    "LinkBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.private & filters.user(ADMIN_ID) & (filters.document | filters.video | filters.audio | filters.photo))
async def handle_admin_file(client: Client, message: Message):
    try:
        await message.reply_text("फ़ाइल चैनल में स्टोर हो रही है... कृपया प्रतीक्षा करें।")
        
        forwarded_msg = await message.copy(CHANNEL_ID)
        
        message_id = forwarded_msg.id
        deep_link = f"https://t.me/{BOT_USERNAME}?start={message_id}"
        
        await message.reply_text(
            f"✅ **सफलतापूर्वक स्टोर हो गई!**\n\n"
            f"यह आपकी Deep Link है:\n\n"
            f"`{deep_link}`\n\n"
            f"**टेस्ट करने के लिए:** इसे किसी और यूज़र को भेजें।"
        )
        
    except Exception as e:
        await message.reply_text(
            f"❌ फ़ाइल प्रोसेस करते समय एक त्रुटि हुई:\n"
            f"**{e}**\n\n"
            f"अगर त्रुटि 'Peer id invalid' है, तो सुनिश्चित करें कि बॉट चैनल में 'Post Messages' की अनुमति के साथ एडमिन है।"
        )

# 1. सामान्य /start कमांड (कोई payload नहीं) के लिए नया हैंडलर
@app.on_message(filters.private & filters.regex("^/start$|^/start@" + BOT_USERNAME + "$"))
async def handle_simple_start(client: Client, message: Message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Channel Link 🔗", url=CHANNEL_LINK)]
    ])

    welcome_text = (
        "✨ __**Welcome to the File Link Bot**__ ✨\n\n"
        "**फ़ाइलों के लिए, कृपया हमारे चैनल से प्राप्त विशेष लिंक का उपयोग करें।**\n\n"
        "यह लिंक आपको सीधे आपकी फ़ाइल तक पहुँचा देगा!\n"
        "नीचे दिए गए बटन से हमारे चैनल को जॉइन करें और विशेष लिंक प्राप्त करें:"
    )
    
    is_admin = message.from_user.id == ADMIN_ID
    if is_admin:
        welcome_text += (
            "\n\n**👑 एडमिन नोटिस:**\n"
            "फ़ाइल का लिंक बनाने के लिए, मुझे कोई भी फ़ाइल भेजें।"
        )
    
    await message.reply_text(
        welcome_text,
        reply_markup=keyboard,
        parse_mode="markdown" 
    )

# 2. Deep Link /start <payload> के लिए हैंडलर
@app.on_message(filters.private & filters.command("start") & ~filters.regex("^/start$|^/start@" + BOT_USERNAME + "$"))
async def handle_deep_link_start(client: Client, message: Message):
    
    # सुनिश्चित करें कि payload मौजूद है
    if len(message.command) < 2:
        return 
        
    payload = message.command[1]
    
    try:
        message_id = int(payload)
        
        await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=CHANNEL_ID,
            message_id=message_id
        )
        
        await message.reply_text(
            "🎉 **Done!** आपकी requested फ़ाइल भेज दी गई है।\n"
            "अगर फ़ाइल न दिखे, तो थोड़ा इंतज़ार करें।\n\n",
            parse_mode="markdown"
        )
        
    except ValueError:
        # अगर payload संख्या नहीं है (हो सकता है कोई कस्टम deep link हो)
        await message.reply_text("नमस्ते! अमान्य Deep Link ID।")
        
    except Exception as e:
        # अगर फ़ाइल मौजूद नहीं है
        await message.reply_text(
            "❌ **क्षमा करें!** यह फ़ाइल अब उपलब्ध नहीं है या लिंक एक्सपायर हो गया है।"
        )


flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return jsonify({"status": "Bot is running", "platform": "Replit"}), 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    app.run()
        
