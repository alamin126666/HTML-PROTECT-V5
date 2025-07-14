import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from html import escape, unescape

TOKEN = os.getenv("TOKEN")
user_state = {}

protect_keyboard = ReplyKeyboardMarkup(
    [["🔴 HTML PROTECT ON 🔴"], ["🟢 HTML PROTECT OFF 🟢"]],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**⛔ আপনি এই বোট দিয়ে এইচটিএমএল কোড প্রটেক্ট করতে পারবেন এবং প্রটেক্ট ভাঙতে পারবেন।**",
        reply_markup=protect_keyboard,
        parse_mode="Markdown"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if "PROTECT ON" in text:
        user_state[user_id] = "protect"
        await update.message.reply_text("⭕ UPLOAD YOUR HTML ⬇️")
    elif "PROTECT OFF" in text:
        user_state[user_id] = "deprotect"
        await update.message.reply_text("⭕ UPLOAD YOUR HTML ⬇️")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_state:
        await update.message.reply_text("⚠️ প্রথমে Protect ON বা OFF নির্বাচন করুন।")
        return

    file = await update.message.document.get_file()
    file_path = f"{user_id}_{update.message.document.file_name}"
    await file.download_to_drive(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    if user_state[user_id] == "protect":
        protected = escape(html_content)
        output_file = f"{user_id}_protected.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"<!-- PROTECTED HTML -->\n<pre>{protected}</pre>")
        await update.message.reply_document(document=open(output_file, "rb"), filename="protected.html")
    elif user_state[user_id] == "deprotect":
        try:
            unprotected = unescape(html_content)
            output_file = f"{user_id}_unprotected.html"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(unprotected)
            await update.message.reply_document(document=open(output_file, "rb"), filename="unprotected.html")
        except:
            await update.message.reply_text("❌ ডিকোড করতে ব্যর্থ।")

    os.remove(file_path)
    if os.path.exists(output_file):
        os.remove(output_file)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    print("🤖 Bot is running...")
    app.run_polling()