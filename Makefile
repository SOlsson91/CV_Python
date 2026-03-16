.PHONY: setup run clean

VENV := .venv
PY := $(VENV)/bin/python
DATA ?= cv.yml

setup:
	python3 -m venv $(VENV)
	$(PY) -m pip install --upgrade pip -q
	$(PY) -m pip install -r requirements.txt
	@echo "Done! Run 'make run' to generate the PDF."

run:
	$(PY) cv_generator.py $(DATA)

clean:
	rm -rf $(VENV)
