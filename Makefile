include .env

run:
	@poetry run python3 authproxy/__main__.py

generate:
	@edgedb-py --file db.py
