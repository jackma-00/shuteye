from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)
from datetime import datetime

from src.common.config import (
    BEDTIME,
    EARLIEST_WAKE,
    LATEST_BEDTIME,
    LOG_PATH,
    PLAN_PATH,
    WAKEUP,
    ONSET,
    AWAKE,
    INIT_WINDOW,
    UPDATE_WINDOW,
)
from src.common.exceptions import EntrySaveError, PlanUpdateError

from src.messaging.messages import Messages

from src.data_manager.log_utils import (
    add_new_entry,
    enough_data_for_first_plan,
    read_log_csv,
    ready_for_new_plan,
)
from src.data_manager.plan_utils import update_bedtime, update_wake_time, load_plan

from src.processing.compute_sleep_plan import (
    adjust_sleep_plan_se_tst_conservative,
    initialize_sleep_plan,
)


async def log(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(Messages.good_morning)
    return BEDTIME


async def get_bedtime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        bedtime = datetime.strptime(update.message.text.strip(), "%H:%M").time()
        context.user_data["bedtime"] = bedtime
        await update.message.reply_text(Messages.wake_up_time)
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
        await update.message.reply_text(Messages.ask_onset)
        return ONSET
    except Exception as e:
        await update.message.reply_text(
            f"⚠️ Error parsing wake-up. Please try again (HH:MM)"
        )
        return WAKEUP


async def get_sleep_onset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["onset"] = int(update.message.text)
        await update.message.reply_text(Messages.minutes_awake)
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
            await update.message.reply_text(Messages.first_sleep_plan_prompt)

            return EARLIEST_WAKE

        if ready_for_new_plan():
            # NOTE: ask for bedtime as anchor for new plan
            await update.message.reply_text(Messages.ready_for_next_plan_bedtime)

            return LATEST_BEDTIME

        await update.message.reply_text(Messages.thats_it)

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


async def ask_earliest_wake(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        earliest_wake = datetime.strptime(update.message.text.strip(), "%H:%M").time()
        update_wake_time(earliest_wake)

        await update.message.reply_text(
            Messages.new_plan_being_generated.format(
                wake_time=earliest_wake.strftime("%H:%M")
            )
        )

        # Compute new plan
        df = read_log_csv(LOG_PATH)
        curr_plan = load_plan(PLAN_PATH)
        if len(df) == INIT_WINDOW:
            new_plan = initialize_sleep_plan(df, curr_plan)

            hours, minutes = divmod(new_plan.tib, 60)

            await update.message.reply_text(
                Messages.first_sleep_plan.format(
                    hours=hours,
                    minutes=minutes,
                    bedtime=new_plan.bedtime.strftime("%H:%M"),
                    wake_time=new_plan.wake_time.strftime("%H:%M"),
                )
            )
        else:
            new_plan, avg_se, avg_tst = adjust_sleep_plan_se_tst_conservative(
                df.tail(UPDATE_WINDOW), curr_plan
            )

            hours, minutes = divmod(new_plan.tib, 60)
            hours_tst, minutes_tst = divmod(avg_tst, 60)

            await update.message.reply_text(
                Messages.new_sleep_plan.format(
                    hours=hours,
                    minutes=minutes,
                    bedtime=new_plan.bedtime.strftime("%H:%M"),
                    wake_time=new_plan.wake_time.strftime("%H:%M"),
                    UPDATE_WINDOW=UPDATE_WINDOW,
                    hours_tst=int(hours_tst),
                    minutes_tst=int(minutes_tst),
                    avg_se=avg_se,
                )
            )

        # Stop the bot after final response
        context.application.stop_running()

        return ConversationHandler.END
    except ValueError as e:
        await update.message.reply_text(
            f"⚠️ Error parsing time. Please enter your earliest desired wake-up time (HH:MM): {e}"
        )
        return EARLIEST_WAKE
    except PlanUpdateError as e:
        print(f"PlanUpdateError: {e}")
        await update.message.reply_text(Messages.internal_error)
        # Stop the bot after final response
        context.application.stop_running()

        return ConversationHandler.END


async def ask_latest_bedtime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        latest_bedtime = datetime.strptime(update.message.text.strip(), "%H:%M").time()
        update_bedtime(latest_bedtime)

        await update.message.reply_text(
            Messages.new_plan_being_generated.format(
                wake_time=latest_bedtime.strftime("%H:%M")
            )
        )

        # Compute new plan
        df = read_log_csv(LOG_PATH)
        curr_plan = load_plan(PLAN_PATH)
        new_plan, avg_se, avg_tst = adjust_sleep_plan_se_tst_conservative(
            df.tail(UPDATE_WINDOW), curr_plan
        )

        hours, minutes = divmod(new_plan.tib, 60)
        hours_tst, minutes_tst = divmod(avg_tst, 60)

        await update.message.reply_text(
            Messages.new_sleep_plan.format(
                hours=hours,
                minutes=minutes,
                bedtime=new_plan.bedtime.strftime("%H:%M"),
                wake_time=new_plan.wake_time.strftime("%H:%M"),
                UPDATE_WINDOW=UPDATE_WINDOW,
                hours_tst=int(hours_tst),
                minutes_tst=int(minutes_tst),
                avg_se=avg_se,
            )
        )

        # Stop the bot after final response
        context.application.stop_running()

        return ConversationHandler.END
    except ValueError as e:
        await update.message.reply_text(
            f"⚠️ Error parsing time. Please enter your earliest desired wake-up time (HH:MM): {e}"
        )
        return EARLIEST_WAKE
    except PlanUpdateError as e:
        print(f"PlanUpdateError: {e}")
        await update.message.reply_text(Messages.internal_error)
        # Stop the bot after final response
        context.application.stop_running()

        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(Messages.bye)
    return ConversationHandler.END
