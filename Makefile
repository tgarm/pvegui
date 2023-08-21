.PHONY: run build init

init:
	pip install -r requirements.txt

build:
	pip freeze > requirements.txt


run:
	python3 capp.py
