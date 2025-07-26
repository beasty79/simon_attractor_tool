VENV_NAME := .venv
PYTHON := $(VENV_NAME)/bin/python

.PHONY: venv install clean run

venv:
	python3 -m venv $(VENV_NAME)
	$(VENV_NAME)/bin/pip install --upgrade pip

install: venv
	$(VENV_NAME)/bin/pip install -r requirements.txt

run: install
	$(PYTHON) main.py

clean:
	rm -rf $(VENV_NAME)
