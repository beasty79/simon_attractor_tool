VENV_NAME := .venv
PYTHON := $(VENV_NAME)/bin/python
PIP := $(VENV_NAME)/bin/pip

.PHONY: venv install clean run

venv:
	python3 -m venv $(VENV_NAME)
	$(PIP) install --upgrade pip

install: venv
	$(PIP) install -r requirements.txt;

run: install
	@if [ -f main.py ]; then \
		$(PYTHON) main.py; \
	else \
		echo "❌ main.py not found."; \
		exit 1; \
	fi

clean:
	rm -rf $(VENV_NAME)
