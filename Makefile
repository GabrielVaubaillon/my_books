
library_data=books.yaml
list_directory=Lists/
stats_file=README.md
library_script=Code/src/main.py

.PHONY: update
update:
	$(library_script) $(library_data) $(list_directory) $(stats_file)

.PHONY: clean
clean:
	rm Lists/*

