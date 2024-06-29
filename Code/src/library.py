from pathlib import Path
import re
import strictyaml as yaml
import sys
from typing import Any


class Language:
    def __init__(
        self,
        id: str,
        names: dict[str, str],
    ):
        self.id: str = id
        self.names: dict[str, str] = names


class Work:
    def __init__(
        self,
        key: str,
        titles: dict[str, str],
        language: str,
        read: bool,
        books: set[str] | None,
        authors: set[str] | None,
        notes: str | None,
    ):
        self.key: str = key
        self.titles: dict[str, str] = titles
        self.language: str = language
        self.read: bool = read
        self.books: set[str] = books if books is not None else set()
        self.authors: set[str] = authors if authors is not None else set()
        self.notes: str = notes if notes is not None else ""


class Book:
    def __init__(
        self,
        key: str,
        title: str,
        language: str,
        isbn: str,
        situation: str,
        notes: str | None,
    ):
        self.key: str = key
        self.title: str = title
        self.language: str = language
        self.isbn: str = isbn
        self.situation: str = situation
        self.notes: str = notes if notes is not None else ""


class Author:
    def __init__(
        self,
        key: str,
        name: str,
        sorting_name: str | None,
        notes: str | None,
    ):
        self.key: str = key
        self.name: str = name
        if not sorting_name:
            last_name = re.search(r"\w+$", name)
            if not last_name:
                raise RuntimeError(f"No last name found for {key}, name is {name}")
            sorting_name = last_name.group(0).lower()
        self.sorting_name: str = sorting_name
        self.notes: str = notes if notes is not None else ""


class Serie:
    def __init__(
        self,
        key: str,
        names: dict[str, str],
        abbreviation: str | None,
        works: dict[str, str],
        notes: str | None,
    ):
        self.key: str = key
        self.names: dict[str, str] = names
        self.abbreviation: str = abbreviation if abbreviation is not None else ""
        self.works: dict[str, str] = works
        self.notes: str = notes if notes is not None else ""


class Library:
    def __init__(
        self,
        languages: dict[str, dict[str, str]],
        works: dict[str, Any],
        books: dict[str, Any],
        authors: dict[str, Any],
        series: dict[str, Any],
    ):
        print(f"languages: {languages}")
        print(f"works: {works}")
        print(f"books: {books}")
        print(f"authors: {authors}")
        print(f"series: {series}")

        self.languages: dict[str, Language] = {}
        for lang_key, language_dict in languages.items():
            self.languages[lang_key] = Language(lang_key, language_dict)

        self.works: dict[str, Work] = {}
        for work_key, work in works.items():
            books_list = set(work["books"].split(";")) if work["books"] else None
            authors_list = set(work["authors"]) if work["authors"] else None
            self.works[work_key] = Work(
                key=work_key,
                titles=work["titles"],
                language=work["language"],
                read=work["read"],
                books=books_list,
                authors=authors_list,
                notes=work.get("notes", None),
            )

        self.books: dict[str, Book] = {}
        for book_key, book in books.items():
            self.books[book_key] = Book(
                key=book_key,
                title=book["title"],
                language=book["language"],
                isbn=book["isbn"],
                situation=book["situation"],
                notes=book.get("notes", None),
            )

        self.authors: dict[str, Author] = {}
        for author_key, author in authors.items():
            self.authors[author_key] = Author(
                key=author_key,
                name=author["name"],
                sorting_name=author.get("sorting_name", None),
                notes=author.get("notes", None),
            )

        self.series: dict[str, Serie] = {}
        for serie_key, serie in series.items():
            self.series[serie_key] = Serie(
                key=serie_key,
                names=serie["name"],
                abbreviation=serie.get("abbreviation", None),
                works=serie.get("works", dict()),
                notes=serie.get("notes", None),
            )


def load_library_file(library_yaml: str) -> Library:
    schema = yaml.Map(
        {
            "languages": yaml.MapPattern(yaml.Str(), yaml.MapPattern(yaml.Str(), yaml.Str())),
            "works": yaml.MapPattern(
                yaml.Str(),
                yaml.Map(
                    {
                        "titles": yaml.MapPattern(yaml.Str(), yaml.Str()),
                        "language": yaml.Str(),
                        "read": yaml.Bool(),
                        "books": yaml.Str(),
                        "authors": yaml.Str(),
                        yaml.Optional("notes"): yaml.Str(),
                    }
                ),
            ),
            "books": yaml.MapPattern(
                yaml.Str(),
                yaml.Map(
                    {
                        "title": yaml.Str(),
                        "language": yaml.Str(),
                        "isbn": yaml.Str(),
                        "situation": yaml.Str(),
                        yaml.Optional("notes"): yaml.Str(),
                    }
                ),
            ),
            "authors": yaml.MapPattern(
                yaml.Str(),
                yaml.Map(
                    {
                        "name": yaml.Str(),
                        yaml.Optional("sorting_name"): yaml.Str(),
                        yaml.Optional("notes"): yaml.Str(),
                    }
                ),
            ),
            "series": yaml.MapPattern(
                yaml.Str(),
                yaml.Map(
                    {
                        "name": yaml.MapPattern(yaml.Str(), yaml.Str()),
                        yaml.Optional("works"): yaml.MapPattern(yaml.Str(), yaml.Str()),
                        yaml.Optional("abbreviation"): yaml.Str(),
                        yaml.Optional("subseries"): yaml.MapPattern(yaml.Str(), yaml.Str()),
                        yaml.Optional("notes"): yaml.Str(),
                    }
                ),
            ),
        }
    )

    yaml_library = yaml.load(library_yaml, schema)

    # Extensive checks should be made on yaml object (keep info about line, comments, etc.)

    library_dict: dict[str, Any] = yaml_library.data  # pyright:ignore

    library = Library(
        languages=library_dict["languages"],
        works=library_dict["works"],
        books=library_dict["books"],
        authors=library_dict["authors"],
        series=library_dict["series"],
    )
    return library


def test() -> None:
    test_filepath = Path("test/books.yaml")
    with open(test_filepath, "r", encoding="utf-8") as file:
        library_yaml = file.read()
    load_library_file(library_yaml)
    sys.exit(0)


if __name__ == "__main__":
    test()
