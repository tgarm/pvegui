.PHONY: run build init

init:
	pip install -r requirements.txt

build:
	pip freeze > requirements.txt

dist:
	pyinstaller --onefile capp.py

run:
	python3 capp.py
