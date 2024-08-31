files := src

bin=.venv/bin
python=$(bin)/python

.PHONY: lint
lint: .venv
	$(bin)/pylint $(files); \
	$(bin)/mypy $(files); \
	$(bin)/black --check --line-length=100 $(files);

.PHONY: init
init: .venv
	python -m venv .venv
	$(bin)/pip install -r requirement.txt

.PHONY: clean
clean: .venv
	# TODO: remove .venv, __pycache__

.PHONY: format
format: .venv
	$(bin)/black --line-length=100 $(files)

.venv:
	python -m venv .venv; \
	$(bin)/pip install -r requirement.txt

