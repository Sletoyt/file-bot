from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import os
import threading
from flask import Flask

# --- Configuration (यह जानकारी सीधे आपके द्वारा दी गई है) ---
API_ID = 16267139
API_HASH = "e0bdab938a5b5d771411f45ee12a9f2b"
BOT_TOKEN = "8347361707:AAHGPqpYoSqfKeex_QSvb6Wgg-BjeXD7Q10"
BOT_USERNAME = "adultvideofree_bot"
ADMIN_ID = 7843231115
CHANNEL_ID = -1002714387561

# --- Pyrogram Client Initialization ---
app = Client(
    "DeepLinkBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# --- Message 1: Regular /start Command ---
regular_start_text = (
    "**नमस्ते!** 👋\n\n"
    "यह एक **स्पेशल फ़ाइल लिंक बॉट** है।\n"
    "फ़ाइल प्राप्त करने के लिए, कृपया **स्पेशल लिंक** का उपयोग करें जो आपको हमारे चैनल से मिलेगा।\n\n"
    "लिंक नीचे बटन में दिया गया है। **बेहतरीन फ़ॉन्ट** के लिए हमने Markdown का उपयोग किया है।"
)

# Channel Link Button
channel_link_button = InlineKeyboardMarkup([
    [InlineKeyboardButton("हमारा चैनल ज्वाइन करें (स्पेशल लिंक)", url="https://t.me/+fnk2mum5ClNhMWM9")]
])

@app.on_message(filters.command("start"))
async def start_command_handler(client, message):
    if len(message.command) > 1:
        # Deep Link Start: /start payload
        payload = message.command[1]
        try:
            file_message_id = int(payload)
            
            # File को चैनल से यूजर को Forward करें
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=CHANNEL_ID,
                message_id=file_message_id
            )
            
            # Message 2: Success Message
            deep_start_success_text = "**✅ Done!**\n\nआपकी फ़ाइल भेज दी गई है।"
            await message.reply_text(
                deep_start_success_text,
                parse_mode=ParseMode.MARKDOWN
            )

        except ValueError:
            await message.reply_text("क्षमा करें, यह एक अमान्य फ़ाइल कोड है।")
        except Exception as e:
            await message.reply_text(f"फ़ाइल भेजते समय कोई त्रुटि हुई। शायद यह लिंक अब मान्य नहीं है।")

    else:
        # Regular Start: /start
        await message.reply_text(
            regular_start_text,
            reply_markup=channel_link_button,
            parse_mode=ParseMode.MARKDOWN
        )


# --- File Upload Handling (Only for Admin) ---
@app.on_message(filters.media & filters.user(ADMIN_ID))
async def file_handler(client, message):
    try:
        # 1. File को Private Channel में Forward करें
        forwarded_msg = await client.forward_messages(
            chat_id=CHANNEL_ID,
            from_chat_id=message.chat.id,
            message_ids=message.id
        )
        
        # 2. Forwarded Message की ID निकालें (यह ID परमानेंट है)
        permanent_message_id = forwarded_msg.id
        
        # 3. Deep Link बनाएँ
        deep_link = f"https://t.me/{BOT_USERNAME}?start={permanent_message_id}"
        
        # 4. Link को Admin को भेजें
        response_text = (
            "**✅ फ़ाइल सफलतापूर्वक स्टोर और लिंक हो गई!**\n\n"
            f"**Deep Link:** `{deep_link}`\n\n"
            "यह लिंक सर्वर रीस्टार्ट होने के बाद भी काम करेगा।"
        )
        
        await message.reply_text(
            response_text,
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        await message.reply_text(f"फ़ाइल को चैनल में स्टोर करते समय त्रुटि हुई: {e}")


# --- Replit Hosting के लिए Flask Server ---
# यह छोटा सा Flask कोड Replit को बताता है कि आपका बॉट चालू है, 
# जिससे वह उसे 'हमेशा चालू' (always on) रखता है।
app_server = Flask(__name__)

@app_server.route('/')
def home():
    return "Telegram Bot is Running!"

def run_flask():
    # Flask को 0.0.0.0 पर चलाएं ताकि वह Replit के सर्वर पर एक्सेस हो सके
    app_server.run(host='0.0.0.0', port=8080)

# --- Main Execution ---
def main():
    # Flask Server को एक अलग Thread में शुरू करें
    threading.Thread(target=run_flask).start()
    
    # Bot Client को चलाएं और रोकें नहीं (Idle)
    print("Bot Client Running...")
    app.run()

if __name__ == '__main__':
    main()
            
