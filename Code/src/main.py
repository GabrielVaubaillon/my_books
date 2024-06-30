#!/bin/python
import argparse
from pathlib import Path

import sys

for p in sys.path:
    print(p)

import library

def _parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename", type=str)
    parser.add_argument("output_dir", type=str)
    parser.add_argument("stats_file", type=str)
    return parser.parse_args()

def percent(subset, original_set):
    return f"{len(subset)} ({round(len(subset)/len(original_set)*100, 2)}%)"

def main():
    test_filepath = Path("test/books.yaml")
    with open(test_filepath, "r", encoding="utf-8") as file:
        library_yaml = file.read()
    library_obj = library.load(library_yaml)
    print(library_obj)
    sys.exit(0)

if __name__ == "__main__":
    main()
