test:
	poetry run pytest

format:
	poetry run isort --apply 
	poetry run black abridge tests

lint:
	poetry run pylint abridge
	poetry run pylint --rcfile .pylintrc-tests tests
	poetry run mypy abridge tests
	poetry run black -v --check tests abridge

build:
	poetry build

publish:
	poetry publish