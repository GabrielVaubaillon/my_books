from pathlib import Path
import re
import sys
import textwrap
from typing import Any

import strictyaml as yaml


class Language:
    def __init__(
        self,
        id: str,
        names: dict[str, str],
    ):
        self.id: str = id
        self.names: dict[str, str] = names

    def __str__(self) -> str:
        str_ = f"{self.id}:\n"
        for lang_id, language_name in self.names.items():
            str_ += f"  {lang_id}: {language_name}\n"
        str_ = str_.removesuffix("\n")
        return str_


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

        # Others attributes, created from Library
        self.owned: bool = False
        self.serie_id: str = ""
        self.serie_position: str = ""

    def __str__(self) -> str:
        titles = "\n".join([f"    {lang_id}: {title}" for lang_id, title in self.titles.items()])
        str_ = (
            f"{self.key}:\n"
            f"  titles:\n{titles}\n"
            f"  language: {self.language}\n"
            f"  read: {self.read}\n"
            f"  books: {self.books}\n"
            f"  authors: {self.authors}\n"
            f"  notes: {self.notes}\n"
            f"  serie_id: {self.serie_id}\n"
            f"  serie_position: {self.serie_position}\n"
        )
        str_ = str_.removesuffix("\n")
        return str_


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

        # Others attributes, created from Library
        self.works: set[str] = set()
        self.authors: set[str] = set()
        self.read: None | bool = None

        self.serie_id: str = ""
        self.serie_position: str = ""

    def add_serie(
        self,
        serie_id: str,
        position: str,
    ) -> None:
        """Setting series info for the book.

        Not straightforward because of books having multiple works.
        """
        if not self.serie_id:
            self.serie_id = serie_id
            self.serie_position = position
        elif self.serie_id > serie_id:
            self.serie_id = serie_id
            self.serie_position = position
        elif self.serie_id == serie_id and self.serie_position > position:
            self.serie_position = position

    def __str__(self) -> str:
        str_ = (
            f"{self.key}:\n"
            f"  title: {self.title}\n"
            f"  language: {self.language}\n"
            f"  isbn: {self.isbn}\n"
            f"  works: {self.works}\n"
            f"  authors: {self.authors}\n"
            f"  notes: {self.notes}\n"
            f"  serie_id: {self.serie_id}\n"
            f"  serie_position: {self.serie_position}\n"
        )
        str_ = str_.removesuffix("\n")
        return str_


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

        # Others attributes, created from Library
        self.works: set[str] = set()
        self.books: set[str] = set()

    def __str__(self) -> str:
        str_ = (
            f"{self.key}:\n"
            f"  name: {self.name}\n"
            f"  sorting_name: {self.sorting_name}\n"
            f"  works: {self.works}\n"
            f"  books: {self.books}\n"
            f"  notes: {self.notes}\n"
        )
        str_ = str_.removesuffix("\n")
        return str_


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

    def __str__(self) -> str:
        names = "\n".join([f"    {lang_id}: {name}" for lang_id, name in self.names.items()])
        str_ = (
            f"{self.key}:\n"
            f"  names:\n{names}\n"
            f"  abbreviation: {self.abbreviation}\n"
            f"  works: {self.works}\n"
            f"  notes: {self.notes}\n"
        )
        str_ = str_.removesuffix("\n")
        return str_


class Library:
    def __init__(
        self,
        languages: dict[str, dict[str, str]],
        works: dict[str, Any],
        books: dict[str, Any],
        authors: dict[str, Any],
        series: dict[str, Any],
    ):
        self.languages: dict[str, Language] = {}
        for lang_key, language_dict in languages.items():
            self.languages[lang_key] = Language(lang_key, language_dict)

        self.works: dict[str, Work] = {}
        for work_key, work in works.items():
            books_list = set(work["books"].split(";")) if work["books"] else None
            authors_list = set(work["authors"].split(";")) if work["authors"] else None
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

        # Link works to series
        for serie_id, serie in self.series.items():
            # TODO: check only one series per work
            for position, work_id in serie.works.items():
                self.works[work_id].serie_id = serie_id
                self.works[work_id].serie_position = position

        # Link: books to works, books to authors, books to series,
        #       authors to works, authors to books
        # TODO:
        # TODO: authors to series, series to authors
        for work_id, work in self.works.items():
            owned = False
            for book_id in work.books:
                self.books[book_id].works.add(work_id)
                self.books[book_id].authors |= work.authors
                self.books[book_id].read = work.read
                self.books[book_id].add_serie(serie_id=work.serie_id, position=work.serie_position)
                if self.books[book_id].situation:
                    owned = True
            for author_id in work.authors:
                self.authors[author_id].works.add(work_id)
                self.authors[author_id].books |= work.books
            work.owned = owned

        # set of all situations
        self.situations: set[str] = {
            book.situation
            for book in self.books.values()
            if book.situation
            and (not book.situation.startswith("Prêté"))
            and ("/" not in book.situation)
        }

    def __str__(self) -> str:
        str_list = []

        str_list.append("languages:")
        str_list.append(
            textwrap.indent(
                "\n".join([str(language) for language in self.languages.values()]), "  "
            )
        )
        str_list.append("works:")
        str_list.append(
            textwrap.indent("\n".join([str(work) for work in self.works.values()]), "  ")
        )
        str_list.append("books:")
        str_list.append(
            textwrap.indent("\n".join([str(book) for book in self.books.values()]), "  ")
        )
        str_list.append("authors:")
        str_list.append(
            textwrap.indent("\n".join([str(author) for author in self.authors.values()]), "  ")
        )
        str_list.append("series:")
        str_list.append(
            textwrap.indent("\n".join([str(serie) for serie in self.series.values()]), "  ")
        )

        return "\n".join(str_list)


def load(library_yaml: str) -> Library:
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
    library = load(library_yaml)
    print(library)
    sys.exit(0)


if __name__ == "__main__":
    test()
