# bot.py — requires: pip install python-telegram-bot==22.3
import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import Forbidden
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# === YOUR SETTINGS ===
BOT_TOKEN  = "7264360998:AAHLAEn1n5XFbx2q6y4uN52SSsifQjH05KY"   # consider revoking & replacing later for safety
ADMIN_ID   = 893594864                   # your Telegram user ID
CHANNEL_ID = -1002998769375              # your channel numeric ID
PAY_NUMBER = "0616705636"                # where users send the $10
BOT_HANDLE = "@xafiiska_diwaan_galintabot"

# === START COMMAND ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"**Ku soo dhawow 252 College!** 🎓\n\n"
        "Bot-kan waxa uu kaa caawinayaa **isdiiwaan-gelinta**.\n\n"
        f"💵 Qiimaha: **$10**\n"
        f"📲 Ku bixi lambarka: `{PAY_NUMBER}`\n\n"
        "Kadib soo geli **sawirka caddeynta lacag bixinta** (receipt).\n\n"
        "👉 Marka admin uu hubiyo oo ansixiyo, waxaad heli doontaa "
        "**link gaar ah** oo laguugu soo dirayo (hal mar oo kaliya la isticmaali karo, kana shaqayn doona 10 daqiiqo)."
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# === HANDLE RECEIPT (USER SENDS IMAGE/TEXT/DOC/VIDEO) ===
# Copies the exact user message to ADMIN, then sends Approve/Reject buttons.
async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    src_chat_id = update.effective_chat.id
    src_msg_id  = update.effective_message.message_id

    # 1) Copy the original message (keeps photos/text/files/videos) to ADMIN
    copied = None
    try:
        copied = await context.bot.copy_message(
            chat_id=ADMIN_ID,
            from_chat_id=src_chat_id,
            message_id=src_msg_id
        )
    except Forbidden:
        # Happens if ADMIN hasn't pressed Start on the bot yet
        await update.message.reply_text(
            "Fadlan u sheeg admin-ka inuu hal mar riixo **Start** ee bot-ka si farriimaha loo gudbiyo.",
            parse_mode="Markdown"
        )

    # 2) Send admin controls (reply to the copied msg if available)
    kb = [[
        InlineKeyboardButton("✅ Ansixi", callback_data=f"approve:{user.id}"),
        InlineKeyboardButton("❌ Diid",    callback_data=f"reject:{user.id}")
    ]]
    if copied:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Codsi cusub: @{user.username or user.id}\nUser ID: {user.id}\nBot: {BOT_HANDLE}",
            reply_markup=InlineKeyboardMarkup(kb),
            reply_to_message_id=copied.message_id
        )
    else:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Codsi cusub (lama koobiyeeyn fariinta asalka ah): @{user.username or user.id}\nUser ID: {user.id}\nBot: {BOT_HANDLE}",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    # 3) Acknowledge to the sender
    await update.message.reply_text("Mahadsanid! Admin ayaa hubin doona.")

# === ADMIN ACTIONS (APPROVE / REJECT) ===
async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    action, uid = q.data.split(":")
    uid = int(uid)
    if action == "approve":
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        link = await context.bot.create_chat_invite_link(
            chat_id=CHANNEL_ID, expire_date=expire, member_limit=1
        )
        await context.bot.send_message(
            uid,
            f"✅ Waa la ansixiyay!\nKu soo biir (10 daqiiqo, hal isticmaal): {link.invite_link}"
        )
        await q.edit_message_text("Approved ✔️")
    else:
        await context.bot.send_message(uid, "❌ Caddeynta lama ansixin.")
        await q.edit_message_text("Rejected ✖️")

# === MAIN ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))

    # Treat photo/doc/video/animation or non-command text as a potential receipt
    media_filters = (filters.PHOTO | filters.Document.ALL | filters.VIDEO | filters.ANIMATION)
    app.add_handler(MessageHandler((media_filters | (filters.TEXT & ~filters.COMMAND)), handle_receipt))

    # Admin approve/reject buttons
    app.add_handler(CallbackQueryHandler(admin_action, pattern="^(approve|reject):"))

    app.run_polling()

if __name__ == "__main__":
    main()
