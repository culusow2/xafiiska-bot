# pip install python-telegram-bot==22.3
import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# === BOT CONFIGURATION ===
BOT_TOKEN   = "7264360998:AAE9IGyAS7_WDAUIwxcHLIWB6FRpx0oRGXo"  # ⚠️ Replace with a fresh token later (keep secret!)
ADMIN_ID    = 893594864                  # your Telegram user ID
CHANNEL_ID  = -1002998769375             # your channel numeric ID
PAY_NUMBER  = "0616705636"               # your payment number
BOT_HANDLE  = "@xafiiska_diwaan_galintabot"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        f"**Isdiiwaan-gelin – $10**\n\n"
        f"Ku bixi: `{PAY_NUMBER}`\n\n"
        "Kadib soo geli **sawirka caddeynta** (receipt).\n"
        "Marka admin uu ansixiyo → waxaad heli doontaa **link gaar ah** "
        "(hal isticmaal, 10 daqiiqo)."
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# Handle payment proof
async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    kb = [[
        InlineKeyboardButton("✅ Ansixi", callback_data=f"approve:{user.id}"),
        InlineKeyboardButton("❌ Diid",    callback_data=f"reject:{user.id}")
    ]]
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(f"Codsi cusub oo ka yimid @{user.username or user.id}\n"
              f"User ID: {user.id}\nBot: {BOT_HANDLE}"),
        reply_markup=InlineKeyboardMarkup(kb)
    )
    await update.message.reply_text("Mahadsanid! Admin ayaa hubin doona.")

# Admin approves/rejects
async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    action, uid = q.data.split(":")
    uid = int(uid)
    if action == "approve":
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        link = await context.bot.create_chat_invite_link(
            chat_id=CHANNEL_ID,
            expire_date=expire,
            member_limit=1
        )
        await context.bot.send_message(
            uid,
            f"✅ Waa la ansixiyay!\n"
            f"Ku soo biir (10 daqiiqo, hal isticmaal): {link.invite_link}"
        )
        await q.edit_message_text("Approved ✔️")
    else:
        await context.bot.send_message(uid, "❌ Caddeynta lama ansixin.")
        await q.edit_message_text("Rejected ✖️")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), handle_receipt))
    app.add_handler(CallbackQueryHandler(admin_action, pattern="^(approve|reject):"))
    app.run_polling()

if __name__ == "__main__":
    main()
