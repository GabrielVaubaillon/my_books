#!/bin/python
import argparse
from pathlib import Path

import library as lib
from stat_file import write_stat_file
from collections_management import create_collections, dump_collections


def _parse_cli_args():
    # TODO: add descriptions
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("output_stat_file", type=Path)
    return parser.parse_args()


def main(input_file: Path, output_dir: Path, output_stats_file: Path) -> None:

    with open(input_file, mode="r", encoding="utf-8") as file:
        library_yaml = file.read()

    library = lib.load(library_yaml)

    collections = create_collections(library)

    for name, collection in collections.items():
        print(f"{name}: {len(collection)}")

    # Write files
    dump_collections(library, collections, output_dir)

    # Write Readme with library stats and links
    write_stat_file(
        collections=collections,
        collections_files_dir=output_dir,
        output_file=output_stats_file,
        lang=library.languages,
        owned_languages=library.owned_languages,
        situations=library.situations,
    )


if __name__ == "__main__":
    cli_args = _parse_cli_args()
    main(
        input_file=cli_args.input_filename,
        output_dir=cli_args.output_dir,
        output_stats_file=cli_args.output_stat_file,
    )
