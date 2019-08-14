test:
	poetry run pytest

format:
	poetry run isort --apply && poetry run black poshsplice tests

lint:
	poetry run pylint poshsplice && poetry run pylint --rcfile .pylintrc-tests tests && black -v --check tests poshsplice

build:
	poetry build

publish:
	poetry publish