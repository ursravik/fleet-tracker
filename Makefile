.PHONY: init install run test clean

VENV_DIR := .venv

init:
	@echo "👉 Creating virtual environment..."
	python3 -m venv $(VENV_DIR)
	@echo "✅ Virtual environment created in $(VENV_DIR)"

install: init
	@echo "👉 Activating venv and installing dependencies..."
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r requirements.txt
	@echo "✅ Dependencies installed"

run:
	@echo "👉 Running Flask app..."
	FLASK_APP=app.py FLASK_ENV=development $(VENV_DIR)/bin/flask run

test:
	@echo "👉 Running test suite..."
	$(VENV_DIR)/bin/python -m unittest discover tests

clean:
	@echo "🧹 Cleaning up..."
	rm -rf $(VENV_DIR)

