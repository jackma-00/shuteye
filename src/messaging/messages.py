class Messages:
    good_morning = """Good morning! 🌅 I hope you had a restful night. 🌸
What time did you head to bed last night? 🛏️ (HH:MM)"""

    wake_up_time = """Rise and shine! ☀️ What time did you wake up today? ⏰ (HH:MM)"""

    ask_onset = """About how many minutes did it take you to fall asleep? 😴"""

    minutes_awake = (
        """Do you remember how many minutes you were awake during the night? 🌙"""
    )

    first_sleep_plan_prompt = """🎉 Great job! You've logged enough data for your very first sleep plan.
What’s the earliest time you'd like to wake up? (HH:MM)"""

    ready_for_next_plan = """🔄 Awesome! You've collected enough new data for an updated sleep plan.
Would you like to keep the same wake-up time or set a new one? (HH:MM)"""

    # NOTE: This message version is specifically for when the user wants to use the bedtime as an anchor.
    ready_for_next_plan_bedtime = """🔄 Awesome! You've collected enough new data for an updated sleep plan.
Would you like to keep the same bedtime or set a new one? (HH:MM)"""

    thats_it = """That’s all for today! 👋 You can log again tomorrow with /log.
Wishing you a calm and cozy day ahead. ✨"""

    new_plan_being_generated = """Great! Your earliest desired wake-up time is set to {wake_time}.
Your personalized sleep plan is on its way. 🛌💤"""

    first_sleep_plan = """🆕 Your first sleep plan is ready! Here are your details:
- Target Time in Bed (TIB): {hours} hours {minutes} minutes
- Bedtime: {bedtime}
- Wake-up Time: {wake_time}

Wishing you sweet dreams and gentle mornings. 😴✨"""

    new_sleep_plan = """🆕 Your updated sleep plan is here! Here’s what we’ve got:
- Target Time in Bed (TIB): {hours} hours {minutes} minutes
- Bedtime: {bedtime}
- Wake-up Time: {wake_time}
- Average Total Sleep Time (TST) over the last {UPDATE_WINDOW} days: {hours_tst} hours {minutes_tst} minutes
- Average Sleep Efficiency (SE): {avg_se:.2f}%

Keep it up — you’re doing wonderfully! 🌟"""

    bye = """Bye for now! 👋 Hope to see you again soon. Wishing you rest and energy. 😊"""

    internal_error = """❌ Failed to update sleep plan due to an internal error.
Sorry for the inconvenience, we'll fix it soon!"""
