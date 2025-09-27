.PHONY: venv install format lint test local_launch

venv:
	python3 -m venv .shuteye

install:
	source ./.shuteye/bin/activate && \
	python -m pip install --upgrade pip && \
    pip install -r requirements.txt

format:
	source ./.shuteye/bin/activate && \
	black .

lint:
	source ./.shuteye/bin/activate && \
	black --check . && \
	pylint -j 0 --disable=C,W ./src/

# test: venv install
# 	source ./.shuteye/bin/activate && \
# 	pytest .

telegram:
	source ./.shuteye/bin/activate && \
	python -m src.messaging.bot

process:
	source ./.shuteye/bin/activate && \
	python -m src.processing.compute_sleep_plan
