import pandas as pd
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)
from datetime import datetime

from src.common.config import BEDTIME, WAKEUP, ONSET, AWAKE
from src.common.exceptions import EntrySaveError

from src.messaging.logging_utils import add_new_entry


async def log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today_str = datetime.now().strftime("%Y-%m-%d")
    context.user_data["date"] = today_str

    await update.message.reply_text(
        "Good morning! 🌅 Hope you slept well. 🌸 What time did you head to bed? 🛏️ (HH:MM)"
    )
    return BEDTIME


async def get_bedtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        t_bed = pd.to_datetime(update.message.text, format="%H:%M")
        context.user_data["bedtime"] = t_bed
        await update.message.reply_text("What time did you wake up? ⏰ (HH:MM)")
        return WAKEUP
    except Exception as e:
        await update.message.reply_text(
            f"⚠️ Error parsing bedtime. Please try again (HH:MM)"
        )
        return BEDTIME


async def get_wakeup_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        t_wake = pd.to_datetime(update.message.text, format="%H:%M")
        context.user_data["wakeup"] = t_wake
        await update.message.reply_text(
            "How many minutes did it take you to fall asleep?"
        )
        return ONSET
    except Exception as e:
        await update.message.reply_text(
            f"⚠️ Error parsing wake-up. Please try again (HH:MM)"
        )
        return WAKEUP


async def get_sleep_onset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        onset = int(update.message.text)
        context.user_data["onset"] = onset
        await update.message.reply_text(
            "How many minutes were you awake during the night?"
        )
        return AWAKE
    except ValueError:
        await update.message.reply_text(
            "⚠️ Please enter a valid number for sleep onset (minutes)."
        )
        return ONSET


async def get_awaken_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        awake = int(update.message.text)
        context.user_data["awake"] = awake

        # Save entry to CSV
        response = add_new_entry(
            context.user_data["date"],
            context.user_data["bedtime"],
            context.user_data["wakeup"],
            context.user_data["onset"],
            context.user_data["awake"],
        )

        await update.message.reply_text(response)
        
        # Stop the bot after final response
        context.application.stop_running()

        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text(
            "⚠️ Please enter a valid number for awake minutes."
        )
        return AWAKE
    except EntrySaveError as e:
        # optional: log to file or console for debugging
        print(f"EntrySaveError: {e}")
        await update.message.reply_text(
            "❌ Failed to save entry. Please retry with /log"
        )
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Bye! Hope to see you soon 😊")
    return ConversationHandler.END
