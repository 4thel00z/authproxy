include .env

run:
	@poetry run python3 authproxy/__main__.py

generate:
	@poetry run edgedb-py --file db.py

test:
	@poetry run pytest

clean:
	@rm -rf **/__pycache__

