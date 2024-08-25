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


def create_collections(library: lib.Library):
    # TODO: Add authors, and original languages
    # TODO: change that. I'm not happy with this part
    collections = {
        "all_w": set(library.works.keys()),
        "all_b": set(library.books.keys()),
        "all_a": set(library.authors.keys()),
        "owned_w": {id for id, work in library.works.items() if work.owned},
        "owned_b": {id for id, book in library.books.items() if book.situation},
        "read_w": {id for id, work in library.works.items() if work.read},
        "read_b": {id for id, book in library.books.items() if book.read},
        "read_owned_w": {id for id, work in library.works.items() if work.read and work.owned},
        "read_owned_b": {id for id, book in library.books.items() if book.read and book.situation},
        "unread_owned_w": {
            id for id, work in library.works.items() if (not work.read) and work.owned
        },
        "unread_owned_b": {
            id for id, book in library.books.items() if (not book.read) and book.situation
        },
        "read_not_owned_w": {
            id for id, work in library.works.items() if work.read and (not work.owned)
        },
    }
    # languages
    languages = {"fr", "en"}
    for language in languages:
        collections[f"owned_{language}_b"] = {
            id for id, book in library.books.items() if book.language == language and book.situation
        }
    collections[f"owned_other_language_b"] = {
        id
        for id, book in library.books.items()
        if (book.language not in languages) and book.situation
    }

    # situations
    for situation in library.situations:
        collections[f"owned_{situation}_b"] = {
            id for id, book in library.books.items() if book.situation.startswith(situation)
        }
        collections[f"read_owned_{situation}_b"] = {
            id
            for id, book in library.books.items()
            if book.situation.startswith(situation) and book.read
        }
        collections[f"unread_owned_{situation}_b"] = {
            id
            for id, book in library.books.items()
            if book.situation.startswith(situation) and (not book.read)
        }
        for language in languages:
            collections[f"owned_{language}_{situation}_b"] = {
                id
                for id, book in library.books.items()
                if book.situation.startswith(situation) and book.language == language
            }
        collections[f"owned_other_language_{situation}_b"] = {
            id
            for id, book in library.books.items()
            if book.situation.startswith(situation) and book.language not in languages
        }

    return collections


def main(input_file: Path) -> None:

    with open(input_file, "r", encoding="utf-8") as file:
        library_yaml = file.read()

    library = lib.load(library_yaml)

    print(library)

    collections = create_collections(library)

    print(collections.keys())

    # Write files

    # Write Readme


if __name__ == "__main__":
    cli_args = _parse_cli_args()
    main(
        input_file=cli_args.input_filename,
    )
