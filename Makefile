# Local development Makefile

# Environment variables for local development
export TELEGRAM_BOT_TOKEN=8461014766:AAFJpElPtdaSUUU_sYIWeSeP8so_7aOEwH4
export TELEGRAM_CHAT_ID=7225394380
export TEST_LOG_PATH=test_data/log.csv
export TEST_PLAN_PATH=test_data/plan.json

.PHONY: venv install format lint test local_launch

venv:
	python3 -m venv .shuteye

install:
	source ./.shuteye/bin/activate && \
	python -m pip install --upgrade pip && \
    pip install -r requirements.txt

format:
	source ./.shuteye/bin/activate && \
	black src/

lint:
	source ./.shuteye/bin/activate && \
	black --check src/ && \
	pylint -j 0 --disable=C,W src/

# test: venv install
# 	source ./.shuteye/bin/activate && \
# 	pytest .

telegram:
	source ./.shuteye/bin/activate && \
	python -m src.messaging.bot

process:
	source ./.shuteye/bin/activate && \
	python -m src.processing.compute_sleep_plan
