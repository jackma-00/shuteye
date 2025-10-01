# ShutEye Project Documentation

## Overview
ShutEye is a personal sleep management and logging tool designed to help users track their sleep patterns, generate personalized sleep plans, and interact with a Telegram bot for daily logging and feedback. The project is structured for extensibility and clarity, with a focus on Cognitive Behavioral Therapy for Insomnia (CBTI) principles.

---

## Project Structure

```
shuteye/
├── Makefile                # Automation commands
├── requirements.txt        # Python dependencies
├── data/                   # User data and schemas
│   ├── log.csv             # Sleep log data
│   ├── plan.json           # Sleep plan data
│   └── schema.md           # Data schema documentation
├── docs/                   # Documentation and therapist materials
│   ├── algo.md             # Algorithm details
│   └── CBTI-M Therapist Materials.pdf
├── src/                    # Source code
│   ├── __init__.py
│   ├── common/             # Shared utilities and models
│   │   ├── __init__.py
│   │   ├── config.py       # Configuration management
│   │   ├── exceptions.py   # Custom exceptions
│   │   └── models.py       # Data models
│   ├── data_manager/       # Data handling utilities
│   │   ├── log_utils.py    # Log file utilities
│   │   └── plan_utils.py   # Plan file utilities
│   ├── messaging/          # Telegram bot and messaging logic
│   │   ├── __init__.py
│   │   ├── bot.py          # Telegram bot entry point
│   │   ├── handlers.py     # Message handlers
│   │   └── messages.py     # Message templates
│   ├── processing/         # Core processing logic
│   │   ├── __init__.py
│   │   └── compute_sleep_plan.py # Sleep plan computation
│   └── scripts/            # Utility scripts
│       └── run_bot.sh      # Shell script to run the bot
├── test_data/              # Example/test data
│   ├── log.csv
│   └── plan.json
```

---

## Key Components

### 1. Data Management
- **log.csv**: Stores daily sleep logs (date, sleep/wake times, etc.).
- **plan.json**: Stores the current sleep plan for the user.
- **schema.md**: Documents the structure of log and plan files.

### 2. Source Code
- **common/**: Shared configuration, exception handling, and data models.
- **data_manager/**: Functions for reading/writing logs and plans.
- **messaging/**: Telegram bot logic, message templates, and handlers.
- **processing/**: Core algorithms for generating sleep plans.
- **scripts/**: Helper scripts for running the bot.

### 3. Documentation
- **docs/algo.md**: Details on the sleep plan algorithm.
- **docs/CBTI-M Therapist Materials.pdf**: Reference for CBTI principles.

---

## Quick Start Guide

### Prerequisites
- Python 3.8+
- Telegram account
- Telegram Bot Token (from @BotFather)

### 1. Clone the Repository
```bash
git clone https://github.com/jackma-00/shuteye.git
cd shuteye
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure the Bot
- Copy your Telegram Bot Token.
- Edit `src/common/config.py` and set your bot token (or use environment variables as described in the file).

### 4. Run the Bot
```bash
bash src/scripts/run_bot.sh
```
Or directly:
```bash
python src/messaging/bot.py
```

### 5. Log Daily Sleep Entries via Telegram
- Open Telegram and start a chat with your bot.
- Use the `/log` command or follow the bot's prompts to enter your daily sleep data (e.g., bedtime, wake time, sleep quality).
- The bot will store your entries in `data/log.csv` and update your sleep plan as needed.

### 6. View or Edit Your Sleep Plan
- The current plan is stored in `data/plan.json`.
- You can view or manually edit this file if needed.

---

## Example: Logging a New Entry
1. Open Telegram and send `/log` to your bot.
2. The bot will prompt you for:
   - Date
   - Bedtime
   - Wake time
   - Sleep quality (optional)
3. Your entry is saved and the bot may provide feedback or update your plan.

---

## Troubleshooting
- **Bot not responding?**
  - Check your bot token in `config.py`.
  - Ensure your dependencies are installed.
  - Review logs in the terminal for errors.
- **Data not saving?**
  - Ensure `data/` directory is writable.
  - Check file paths in `config.py`.

---

## Extending the Project
- Add new message handlers in `src/messaging/handlers.py`.
- Update data models in `src/common/models.py`.
- Modify or extend the sleep plan algorithm in `src/processing/compute_sleep_plan.py`.

---

## References
- [CBTI-M Therapist Materials](docs/CBTI-M%20Therapist%20Materials.pdf)
- [Algorithm Details](docs/algo.md)

---

For further help, see the inline code comments and the `docs/` folder.
