#!/bin/python
import argparse
from pathlib import Path

import library as lib


def _parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename", type=str)
    # parser.add_argument("output_dir", type=str)
    # parser.add_argument("stats_file", type=str)
    return parser.parse_args()


def percent(subset, original_set):
    return f"{len(subset)} ({round(len(subset)/len(original_set)*100, 2)}%)"


def main(input_file: Path) -> None:

    with open(input_file, "r", encoding="utf-8") as file:
        library_yaml = file.read()

    library = lib.load(library_yaml)

    print(library)


if __name__ == "__main__":
    cli_args = _parse_cli_args()
    main(
        input_file=cli_args.input_filename,
    )
