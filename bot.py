import os
from telegram import Update, InputFile, helpers
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Bot credentials
API_ID = 16267139
API_HASH = "e0bdab938a5b5d771411f45ee12a9f2b"
BOT_TOKEN = "8347361707:AAHGPqpYoSqfKeex_QSvb6Wgg-BjeXD7Q10"
ADMIN_ID = 7843231115

# Folder to save uploaded files
if not os.path.exists("uploads"):
    os.mkdir("uploads")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with deep link support"""
    args = context.args
    if args:
        file_name = args[0]
        file_path = f"uploads/{file_name}"
        if os.path.exists(file_path):
            await update.message.reply_document(InputFile(file_path))
        else:
            await update.message.reply_text("File not found or deleted.")
    else:
        await update.message.reply_text("Welcome to the File Bot!")

async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file uploads (Admin only)"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Only admin can upload files.")
        return

    if not update.message.document:
        await update.message.reply_text("Please send a file along with /upload command.")
        return

    document = update.message.document
    file_name = document.file_name
    file_path = f"uploads/{file_name}"

    new_file = await document.get_file()
    await new_file.download_to_drive(file_path)

    deep_link = helpers.create_deep_linked_url(context.bot.username, file_name)
    await update.message.reply_text(f"✅ File uploaded successfully!\nDeep Link: {deep_link}")

async def handle_docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document messages directly (Admin only)"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("You are not allowed to upload files.")
        return

    document = update.message.document
    file_name = document.file_name
    file_path = f"uploads/{file_name}"
    file = await document.get_file()
    await file.download_to_drive(file_path)
    
    deep_link = helpers.create_deep_linked_url(context.bot.username, file_name)
    await update.message.reply_text(f"✅ File uploaded!\nDeep link: {deep_link}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("upload", upload))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_docs))
    application.run_polling()

if __name__ == "__main__":
    main()
  
