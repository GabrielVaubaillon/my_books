#!/bin/python
import argparse
from pathlib import Path

import library as lib


def _parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename", type=Path)
    parser.add_argument("output_dir", type=Path)
    # parser.add_argument("stats_file", type=str)
    return parser.parse_args()


def percent(subset, original_set):
    return f"{len(subset)} ({round(len(subset)/len(original_set)*100, 2)}%)"


def create_collections(library: lib.Library) -> dict[str, set[str]]:
    # TODO: Add authors, and original languages
    # TODO: change that. I'm not happy with this part
    collections = {
        "all_w": set(library.works.keys()),
        "all_b": set(library.books.keys()),
        "all_a": set(library.authors.keys()),
        "owned_w": {id for id, work in library.works.items() if work.owned},
        "owned_b": {id for id, book in library.books.items() if book.situation},
        "read_w": {id for id, work in library.works.items() if work.read},
        "read_b": {id for id, book in library.books.items() if book.partial_read},
        "read_owned_w": {id for id, work in library.works.items() if work.read and work.owned},
        "read_owned_b": {
            id for id, book in library.books.items() if book.partial_read and book.situation
        },
        "unread_owned_w": {
            id for id, work in library.works.items() if (not work.read) and work.owned
        },
        "unread_owned_b": {
            id for id, book in library.books.items() if (not book.fully_read) and book.situation
        },
        "read_not_owned_w": {
            id for id, work in library.works.items() if work.read and (not work.owned)
        },
    }
    # languages
    for language in library.owned_languages:
        collections[f"owned_{language}_b"] = {
            id for id, book in library.books.items() if book.language == language and book.situation
        }

    # situations
    for situation in library.situations:
        situation_l = situation.lower()
        collections[f"owned_{situation_l}_b"] = {
            id for id, book in library.books.items() if book.situation.startswith(situation)
        }
        collections[f"read_owned_{situation_l}_b"] = {
            id
            for id, book in library.books.items()
            if book.situation.startswith(situation) and book.partial_read
        }
        collections[f"unread_owned_{situation_l}_b"] = {
            id
            for id, book in library.books.items()
            if book.situation.startswith(situation) and (not book.fully_read)
        }
        for language in library.owned_languages:
            collections[f"owned_{language}_{situation_l}_b"] = {
                id
                for id, book in library.books.items()
                if book.situation.startswith(situation) and book.language == language
            }

    return collections


def setup_output_dir(output_dir: Path):
    if output_dir.is_dir():
        for file in output_dir.glob("*.md"):
            file.unlink()
    else:
        output_dir.mkdir(parents=True, exist_ok=True)


def dump_collections(library: lib.Library, collections: dict[str, set[str]], output_dir: Path):
    setup_output_dir(output_dir)
    # IDEA: put header with format for README line !, then the README just read that?

    # TODO: sort collections
    for name, ids in collections.items():
        file_content: str
        # TODO
        if name.endswith("_w"):
            file_content = library.works_html_table(works_ids=ids)
        elif name.endswith("_b"):
            file_content = library.books_html_table(books_ids=ids)
        elif name.endswith("_a"):
            file_content = ""
        else:
            file_content = ""

        if file_content:
            output_file = output_dir / (name + ".md")
            with open(output_file, mode="w", encoding="utf-8") as file:
                file.write(file_content)


def main(input_file: Path, output_dir: Path) -> None:

    with open(input_file, "r", encoding="utf-8") as file:
        library_yaml = file.read()

    library = lib.load(library_yaml)

    # print(library)
    # print()

    collections = create_collections(library)

    for name, collection in collections.items():
        print(f"{name}: {len(collection)}")

    # Write files
    dump_collections(library, collections, output_dir)

    # Write Readme


if __name__ == "__main__":
    cli_args = _parse_cli_args()
    main(
        input_file=cli_args.input_filename,
        output_dir=cli_args.output_dir,
    )
