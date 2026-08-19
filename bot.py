
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]

# Force-join channels
FORCE_CHANNELS = [
    "@creamy_hub",
    "@lassi_hub",
]

# Source channel
SOURCE_CHANNEL_ID = -1004484071781


WELCOME_TEXT = """Wᴇʟᴄᴏᴍᴇ Tᴏ 2 7 Bᴏᴛ

Yᴏᴜ Nᴇᴇᴅ Tᴏ Sᴜʙꜱᴄʀɪʙᴇ Oᴜʀ Cʜᴀɴɴᴇʟ Tᴏ Wᴀᴛᴄʜ Fʀᴇᴇ Vɪᴅᴇᴏꜱ"""


async def check_membership(user_id, context):
    for channel in FORCE_CHANNELS:
        try:
            member = await context.bot.get_chat_member(
                chat_id=channel,
                user_id=user_id
            )

            if member.status in [
                ChatMemberStatus.LEFT,
                ChatMemberStatus.BANNED,
            ]:
                return False

        except Exception:
            return False

    return True


def join_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                "📢 Join Channel 1",
                url="https://t.me/creamy_hub"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 Join Channel 2",
                url="https://t.me/lassi_hub"
            )
        ],
        [
            InlineKeyboardButton(
                "🔄 TRY AGAIN",
                callback_data="try_again"
            )
        ],
    ]

    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ Invalid video link."
        )
        return

    message_id = context.args[0]

    try:
        message_id = int(message_id)
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid video ID."
        )
        return

    context.user_data["message_id"] = message_id

    joined = await check_membership(user.id, context)

    if not joined:
        await update.message.reply_text(
            WELCOME_TEXT,
            reply_markup=join_keyboard()
        )
        return

    await send_video(update, context, message_id)


async def try_again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = update.effective_user

    message_id = context.user_data.get("message_id")

    if not message_id:
        await query.message.reply_text(
            "❌ Video link expired or invalid."
        )
        return

    joined = await check_membership(user.id, context)

    if not joined:
        await query.answer(
            "❌ Please join both channels first!",
            show_alert=True
        )
        return

    await query.message.delete()

    await context.bot.copy_message(
        chat_id=user.id,
        from_chat_id=SOURCE_CHANNEL_ID,
        message_id=message_id
    )


async def send_video(update, context, message_id):
    await context.bot.copy_message(
        chat_id=update.effective_user.id,
        from_chat_id=SOURCE_CHANNEL_ID,
        message_id=message_id
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        CallbackQueryHandler(
            try_again,
            pattern="^try_again$"
        )
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
