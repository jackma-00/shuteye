import pandas as pd
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)
from datetime import datetime

from src.common.config import (
    BEDTIME,
    EARLIEST_WAKE,
    LOG_PATH,
    PLAN_PATH,
    WAKEUP,
    ONSET,
    AWAKE,
    INIT_WINDOW,
    WINDOW_LENGTH,
)
from src.common.exceptions import EntrySaveError, PlanUpdateError

from src.data_manager.log_utils import (
    add_new_entry,
    enough_data_for_first_plan,
    read_log_csv,
    ready_for_new_plan,
)
from src.data_manager.plan_utils import update_wake_time, load_plan

from src.processing.compute_sleep_plan import adjust_sleep_plan, initialize_sleep_plan


async def log(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Good morning! 🌅 Hope you slept well. 🌸 What time did you head to bed? 🛏️ (HH:MM)"
    )
    return BEDTIME


async def get_bedtime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        bedtime = datetime.strptime(update.message.text.strip(), "%H:%M").time()
        context.user_data["bedtime"] = bedtime
        await update.message.reply_text("What time did you wake up? ⏰ (HH:MM)")
        return WAKEUP
    except Exception as e:
        await update.message.reply_text(
            f"⚠️ Error parsing bedtime. Please try again (HH:MM)"
        )
        return BEDTIME


async def get_wakeup_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        wakeup = datetime.strptime(update.message.text.strip(), "%H:%M").time()
        context.user_data["wakeup"] = wakeup
        await update.message.reply_text(
            "How many minutes did it take you to fall asleep?"
        )
        return ONSET
    except Exception as e:
        await update.message.reply_text(
            f"⚠️ Error parsing wake-up. Please try again (HH:MM)"
        )
        return WAKEUP


async def get_sleep_onset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["onset"] = int(update.message.text)
        await update.message.reply_text(
            "How many minutes were you awake during the night?"
        )
        return AWAKE
    except ValueError:
        await update.message.reply_text(
            "⚠️ Please enter a valid number for sleep onset (minutes)."
        )
        return ONSET


async def get_awaken_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["awake"] = int(update.message.text)
        
        # Save entry to CSV
        response = add_new_entry(
            context.user_data["bedtime"],
            context.user_data["wakeup"],
            context.user_data["onset"],
            context.user_data["awake"],
        )

        await update.message.reply_text(response)

        # Check if enough data for plan generation
        if enough_data_for_first_plan():
            await update.message.reply_text(
                "🎉 You've logged enough data for your first sleep plan! Tell me your earliest desired wake-up time (HH:MM)"
            )

            return EARLIEST_WAKE

        if ready_for_new_plan():
            await update.message.reply_text(
                "🔄 You've logged enough new data for an updated sleep plan! Confirm your wake-up time or update it (HH:MM)"
            )

            return EARLIEST_WAKE

        await update.message.reply_text(
            "That's all for today! 👋🏼 You can log again tomorrow with /log"
        )

        # FIXME: Stop the bot after final response
        # context.application.stop_running()

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


async def ask_earliest_wake(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        earliest_wake = datetime.strptime(update.message.text.strip(), "%H:%M").time()
        update_wake_time(earliest_wake)

        await update.message.reply_text(
            f"Great! Your earliest desired wake-up time is set to {earliest_wake.strftime('%H:%M')}. Your sleep plan will be generated shortly. 🛌💤"
        )

        # Compute new plan
        df = read_log_csv(LOG_PATH)
        curr_plan = load_plan(PLAN_PATH)
        if len(df) == INIT_WINDOW:
            new_plan = initialize_sleep_plan(df, curr_plan)

            hours, minutes = divmod(new_plan.tib, 60)

            await update.message.reply_text(
                f"""🆕 Your first sleep plan has been generated! Here are the details:
            - Target Time in Bed (TIB): {hours} hours {minutes} minutes
            - Bedtime: {new_plan.bedtime.strftime('%H:%M')}
            - Wake-up Time: {new_plan.wake_time.strftime('%H:%M')}
            Sweet dreams! 😴✨"""
            )
        else:
            new_plan, avg_se = adjust_sleep_plan(df.tail(WINDOW_LENGTH), curr_plan)

            hours, minutes = divmod(new_plan.tib, 60)

            await update.message.reply_text(
                f"""🆕 Your new sleep plan has been generated! Here are the details:
            - Target Time in Bed (TIB): {hours} hours {minutes} minutes
            - Bedtime: {new_plan.bedtime.strftime('%H:%M')}
            - Wake-up Time: {new_plan.wake_time.strftime('%H:%M')}
            - Last {WINDOW_LENGTH} days' Average Sleep Efficiency (SE): {avg_se:.2f}%
            Sweet dreams! 😴✨"""
            )

        # FIXME: Stop the bot after final response
        # context.application.stop_running()

        return ConversationHandler.END
    except ValueError as e:
        await update.message.reply_text(
            f"⚠️ Error parsing time. Please enter your earliest desired wake-up time (HH:MM): {e}"
        )
        return EARLIEST_WAKE
    except PlanUpdateError as e:
        print(f"PlanUpdateError: {e}")
        await update.message.reply_text(
            "❌ Failed to update sleep plan due to an internal error. Sorry for the inconvenience, we'll fix it soon!"
        )
        # FIXME: Stop the bot after final response
        # context.application.stop_running()

        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Bye! Hope to see you soon 😊")
    return ConversationHandler.END
