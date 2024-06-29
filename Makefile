
library_data=books.yaml
list_directory=Lists/
stats_file=README.md
python_executable=Code/.venv/bin/python
library_script=Code/src/main.py

.PHONY: update
update:
	$(python_executable) $(library_script) $(library_data) $(list_directory) $(stats_file)

.PHONY: clean
clean:
	rm Lists/*

