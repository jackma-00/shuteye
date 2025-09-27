from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ConversationHandler,
    CommandHandler,
)

from src.common.config import BOT_TOKEN, BEDTIME, WAKEUP, ONSET, AWAKE

from src.messaging.handlers import (
    log,
    get_bedtime,
    get_awaken_time,
    get_sleep_onset,
    get_wakeup_time,
    cancel,
)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("log", log)],
        states={
            BEDTIME: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_bedtime)],
            WAKEUP: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), get_wakeup_time)
            ],
            ONSET: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_sleep_onset)],
            AWAKE: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_awaken_time)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("Bot ready to receive reply...")
    app.run_polling()


if __name__ == "__main__":
    main()
