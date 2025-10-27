import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from flask import Flask, jsonify
from threading import Thread

# --- 1. अपनी जानकारी यहां भरें (Your Info Here) ---
# NOTE: सुरक्षा के लिए, आपको इन्हें .env फाइल में रखना चाहिए।
# सादगी के लिए, मैं इन्हें सीधे यहां परिभाषित कर रहा हूँ।
API_ID = 16267139
API_HASH = "e0bdab938a5b5d771411f45ee12a9f2b"
BOT_TOKEN = "8347361707:AAHGPqpYoSqfKeex_QSvb6Wgg-BjeXD7Q10"
ADMIN_ID = 7843231115  # आपका Telegram Admin ID
CHANNEL_ID = -1002714387561 # आपका Private Channel ID (स्टोरेज के लिए)
BOT_USERNAME = "adultvideofree_bot" # आपके बॉट का यूजरनेम

# --- 2. Pyrogram क्लाइंट शुरू करें (Initialize Pyrogram Client) ---
# 'LinkBot' session name का उपयोग कर रहे हैं
app = Client(
    "LinkBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# --- 3. एडमिन द्वारा फाइल अपलोड हैंडलर (Admin File Upload Handler) ---
@app.on_message(filters.private & filters.user(ADMIN_ID) & (filters.document | filters.video | filters.audio | filters.photo))
async def handle_admin_file(client: Client, message: Message):
    """
    जब एडमिन कोई फ़ाइल (डॉक्यूमेंट, वीडियो, ऑडियो, फोटो) भेजता है,
    तो उसे चैनल में कॉपी करता है और deep link बनाता है।
    """
    try:
        # फ़ाइल को चैनल में कॉपी करें। इससे original message_id channel में मिलेगा।
        await message.reply_text("फ़ाइल चैनल में स्टोर हो रही है... कृपया प्रतीक्षा करें।")
        
        # message.copy() का उपयोग करें ताकि फ़ाइल Channel में store हो जाए
        forwarded_msg = await message.copy(CHANNEL_ID)
        
        # Deep Link बनाएं: format है t.me/<bot_username>?start=<message_id>
        message_id = forwarded_msg.id
        deep_link = f"https://t.me/{BOT_USERNAME}?start={message_id}"
        
        # एडमिन को deep link भेजें
        await message.reply_text(
            f"✅ **सफलतापूर्वक स्टोर हो गई!**\n\n"
            f"यह आपकी Deep Link है (सर्वर रीस्टार्ट होने पर भी काम करेगी):\n\n"
            f"`{deep_link}`\n\n"
            f"**टेस्ट करने के लिए:** इसे किसी और यूज़र को भेजें या खुद 'Start' करें।"
        )
        
    except Exception as e:
        print(f"Admin file handling error: {e}")
        await message.reply_text(f"फ़ाइल प्रोसेस करते समय एक त्रुटि हुई: {e}")

# --- 4. Deep Link स्टार्ट हैंडलर (Deep Link Start Handler) ---
@app.on_message(filters.private & filters.command("start"))
async def handle_start(client: Client, message: Message):
    """
    यूज़र द्वारा '/start' कमांड को हैंडल करता है।
    अगर payload (message_id) मौजूद है, तो फ़ाइल भेजता है।
    """
    # '/start' कमांड के बाद के payload को निकालें (उदा: 12345)
    if len(message.command) > 1:
        payload = message.command[1]
        
        try:
            message_id = int(payload)
            
            # channel से फ़ाइल को यूज़र को कॉपी करें
            # copy_message का उपयोग करने से यूज़र को Channel का नाम नहीं दिखेगा
            await client.copy_message(
                chat_id=message.chat.id,  # वर्तमान यूज़र
                from_chat_id=CHANNEL_ID, # स्टोरेज चैनल
                message_id=message_id    # deep link से मिला message_id
            )
            
            await message.reply_text(
                "✅ **आपकी रिक्वेस्टेड फ़ाइल हाज़िर है!**\n\n"
                "अगर फ़ाइल न दिखे, तो शायद यह एक बहुत बड़ी फ़ाइल है और Telegram इसे Process कर रहा है।"
            )
            
        except ValueError:
            # अगर payload नंबर नहीं है
            await message.reply_text("नमस्ते! अमान्य Deep Link ID।")
            
        except Exception as e:
            # अगर message_id चैनल में न मिले या कोई और error हो
            print(f"Error fetching file: {e}")
            await message.reply_text(
                "❌ **क्षमा करें!** यह फ़ाइल अब उपलब्ध नहीं है या लिंक एक्सपायर हो गया है।"
            )
            
    else:
        # अगर कोई payload नहीं है (यूज़र ने बस /start किया है)
        is_admin = message.from_user.id == ADMIN_ID
        
        welcome_text = (
            "👋 **नमस्ते! मैं Deep Link Bot हूँ।**\n\n"
            "मैं आपको फाइल की Deep Link बनाकर देता हूँ, जो सर्वर रीस्टार्ट के बाद भी काम करती है।\n\n"
            "**यूज़र गाइड:**\n"
            "1. आपको बस Deep Link पर क्लिक करना है और फ़ाइल मिल जाएगी।\n\n"
        )
        
        if is_admin:
            welcome_text += (
                "**👑 एडमिन मोड सक्रिय:**\n"
                "फ़ाइल का लिंक बनाने के लिए, बस **मुझे** (एडमिन को) कोई भी फ़ाइल भेजें (डॉक्यूमेंट, वीडियो, आदि)। "
                "मैं आपको तुरंत Deep Link वापस भेज दूँगा।"
            )
        
        await message.reply_text(welcome_text)


# --- 5. Flask Keep-Alive सर्वर (Flask Keep-Alive Server for Replit) ---
# Replit को यह बताने के लिए कि बॉट चालू है और इसे बंद न करें।
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    """एक साधारण रूट ताकि Replit को 200 OK Response मिल सके।"""
    return jsonify({"status": "Bot is running", "platform": "Replit"}), 200

def run_flask():
    """Flask को एक अलग थ्रेड में चलाता है।"""
    port = int(os.environ.get('PORT', 8080))
    # '0.0.0.0' पर चलाएं ताकि Replit इसे एक्सेस कर सके
    flask_app.run(host='0.0.0.0', port=port)

# --- 6. मुख्य फ़ंक्शन जो बॉट और सर्वर शुरू करता है (Main function to start bot and server) ---
if __name__ == "__main__":
    print("Starting Flask Keep-Alive server...")
    # Flask सर्वर को एक नए थ्रेड में शुरू करें
    Thread(target=run_flask).start()
    
    print("Starting Telegram Bot...")
    # Pyrogram बॉट को शुरू करें (यह मुख्य थ्रेड में चलता रहेगा)
    app.run()
    
    # यह सुनिश्चित करने के लिए कि बॉट सही ढंग से बंद हो
    print("Bot stopped.")
        
