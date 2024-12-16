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
        books: list[str] | None,
        authors: list[str] | None,
        notes: str | None,
    ):
        self.key: str = key
        self.titles: dict[str, str] = titles
        self.language: str = language
        self.read: bool = read
        self.books: list[str] = books if books is not None else []
        self.authors: list[str] = authors if authors is not None else []
        self.notes: str = notes if notes is not None else ""

        # Others attributes, created from Library
        self.owned: bool = False
        self.serie_id: str = ""
        self.serie_position: str = ""

    def __str__(self) -> str:
        titles = "\n".join([f"    {lang_id}: {title}" for lang_id, title in self.titles.items()])
        str_list = [
            f"{self.key}:",
            f"  titles:{titles}",
            f"  language: {self.language}",
            f"  read: {self.read}",
            f"  books: {self.books}",
            f"  authors: {self.authors}",
            f"  notes: {self.notes}",
            f"  serie_id: {self.serie_id}",
            f"  serie_position: {self.serie_position}",
        ]
        str_ = "\n".join(str_list)
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
        self.works: list[str] = []
        self.authors: list[str] = []
        self.read: dict[str, bool] = dict()
        self.partial_read: bool = False
        self.fully_read: bool = False

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

    def update_read_status(self) -> None:
        self.fully_read = all(self.read.values())
        self.partial_read = any(self.read.values())

    def __str__(self) -> str:
        str_list = [
            f"{self.key}:",
            f"  title: {self.title}",
            f"  language: {self.language}",
            f"  isbn: {self.isbn}",
            f"  works: {self.works}",
            f"  authors: {self.authors}",
            f"  notes: {self.notes}",
            f"  serie_id: {self.serie_id}",
            f"  serie_position: {self.serie_position}",
        ]
        str_ = "\n".join(str_list)
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
            sorting_name = last_name.group(0)
        self.sorting_name: str = sorting_name.lower()
        print(self.name, self.sorting_name)
        self.notes: str = notes if notes is not None else ""

        # Others attributes, created from Library
        self.works: list[str] = []
        self.books: list[str] = []

        self.works_read: int = 0
        self.works_owned: int = 0
        self.books_owned: int = 0

    def __str__(self) -> str:
        str_list = [
            f"{self.key}:",
            f"  name: {self.name}",
            f"  sorting_name: {self.sorting_name}",
            f"  works: {self.works}",
            f"  books: {self.books}",
            f"  notes: {self.notes}",
        ]
        str_ = "\n".join(str_list)
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
        str_list = [
            f"{self.key}:",
            f"  names:\n{names}",
            f"  abbreviation: {self.abbreviation}",
            f"  works: {self.works}",
            f"  notes: {self.notes}",
        ]
        str_ = "\n".join(str_list)
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
            books_list = work["books"].split(";") if work["books"] else None
            authors_list = work["authors"].split(";") if work["authors"] else None
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
        # TODO: authors to series, series to authors
        for work_id, work in self.works.items():
            owned = False
            for book_id in work.books:
                self.books[book_id].works.append(work_id)
                for author in work.authors:
                    if author not in self.books[book_id].authors:
                        self.books[book_id].authors.append(author)
                self.books[book_id].read[work_id] = work.read
                self.books[book_id].add_serie(serie_id=work.serie_id, position=work.serie_position)
                if self.books[book_id].situation:
                    owned = True
            for author_id in work.authors:
                self.authors[author_id].works.append(work_id)
                for book in work.books:
                    if book not in self.authors[author_id].books:
                        self.authors[author_id].books.append(book)
            work.owned = owned

        for author in self.authors.values():
            for work_id in author.works:
                if self.works[work_id].read:
                    author.works_read += 1
                if self.works[work_id].owned:
                    author.works_owned += 1
            for book_id in author.books:
                if self.books[book_id].situation:
                    author.books_owned += 1

        situations: dict[str, int] = {}
        owned_languages: dict[str, int] = {}
        for book in self.books.values():
            book.update_read_status()
            if (
                book.situation
                and (not book.situation.startswith("Prêté"))
                and ("/" not in book.situation)
            ):
                if book.situation not in situations:
                    situations[book.situation] = 1
                else:
                    situations[book.situation] += 1
            if book.language not in owned_languages:
                owned_languages[book.language] = 1
            else:
                owned_languages[book.language] += 1

        # We sort situations by the number of books in the situation
        self.situations: list[str] = list(
            dict(sorted(situations.items(), key=lambda item: item[1], reverse=True)).keys()
        )
        # We sort owned languages by number of books owned in the language
        self.owned_languages: list[str] = list(
            dict(sorted(owned_languages.items(), key=lambda item: item[1], reverse=True)).keys()
        )

    def __str__(self) -> str:
        str_list = []

        str_list.append("languages:")
        str_list.append(
            textwrap.indent(
                "\n".join([str(language) for language in self.languages.values()]), "  "
            )
        )
        str_list.append("")
        str_list.append("works:")
        str_list.append(
            textwrap.indent("\n".join([str(work) for work in self.works.values()]), "  ")
        )
        str_list.append("")
        str_list.append("books:")
        str_list.append(
            textwrap.indent("\n".join([str(book) for book in self.books.values()]), "  ")
        )
        str_list.append("")
        str_list.append("authors:")
        str_list.append(
            textwrap.indent("\n".join([str(author) for author in self.authors.values()]), "  ")
        )
        str_list.append("")
        str_list.append("series:")
        str_list.append(
            textwrap.indent("\n".join([str(serie) for serie in self.series.values()]), "  ")
        )

        return "\n".join(str_list)

    def sort_books_ids(self, ids: set[str]) -> list[str]:
        books_ids: list[str] = list(ids)

        def sorting_key(book_id: str) -> tuple[str, ...]:
            book: Book = self.books[book_id]
            if book.authors:
                author = self.authors[book.authors[0]].sorting_name.lower()
                fullname = self.authors[book.authors[0]].name.lower()
            else:
                author = "zz"
                fullname = "zzz"
            return (
                author,
                fullname,
                book.serie_id,
                book.serie_position,
                book.title,
                book.situation,
            )

        books_ids.sort(key=lambda x: sorting_key(x))
        return books_ids

    def books_html_table(self, books_ids: set[str]) -> str:
        header: list[str] = [
            "<table>",
            "  <thead>",
            "    <tr>",
            "      <th colspan=2>Titre</th>",
            "      <th>Auteur·rice</th>",
            "      <th>Langue</th>",
            "      <th>Lu</th>",
            "      <th>Situation</th>",
            "    </tr>",
            "  </thead>",
            "  <tbody>",
            "",
        ]
        sorted_books_ids: list[str] = self.sort_books_ids(books_ids)
        body: list[str] = [self.book_html_row(book_id) for book_id in sorted_books_ids]
        footer: list[str] = [
            "",
            "  </tbody>",
            "</table>",
        ]
        str_ = "\n".join(header) + textwrap.indent("\n".join(body), "    ") + "\n".join(footer)
        return str_

    def book_html_row(self, book_id: str) -> str:
        book: Book = self.books[book_id]
        row: list[str] = []
        works: list[Work] = [self.works[work_id] for work_id in book.works]

        # Title
        colspan_title: int
        if len(works) == 1 and book.title == works[0].titles[book.language]:
            colspan_title = 2
        else:
            colspan_title = 1

        row.append(f"  <td colspan={colspan_title} rowspan={len(works)}>{book.title}</td>")
        if colspan_title == 1:
            row.append(f"  <td>{works[0].titles[book.language]}</td>")

        # Authors
        authors: list[set[str]] = []
        for work in works:
            authors.append(set(work.authors))
        rowspan_authors: int
        if all(authors_set == authors[0] for authors_set in authors):
            rowspan_authors = len(works)
        else:
            rowspan_authors = 1
        authors_str: str = " / ".join(
            [self.authors[author_id].name for author_id in works[0].authors]
        )
        row.append(f"  <td rowspan={rowspan_authors}>{authors_str}</td>")

        # Language
        row.append(f"  <td rowspan={len(works)}>{book.language}</td>")

        # Read status
        rowspan_read_status: int
        if book.fully_read or (not book.partial_read):
            rowspan_read_status = len(works)
        else:
            rowspan_read_status = 1
        read_status: str = "Lu" if works[0].read else "Pas Lu"
        row.append(f"  <td rowspan={rowspan_read_status}>{read_status}</td>")

        # Situation
        row.append(f"  <td rowspan={len(works)}>{book.situation}</td>")

        # Others rows if multiple works
        for i in range(1, len(works)):
            row.append("</tr>")
            row.append("<tr>")
            row.append(f"  <td>{works[i].titles[book.language]}</td>")
            if rowspan_authors == 1:
                authors_str = " / ".join(
                    [self.authors[author_id].name for author_id in works[i].authors]
                )
                row.append(f"  <td>{authors_str}</td>")
            if rowspan_read_status == 1:
                read_status = "Lu" if works[i].read else "Pas Lu"
                row.append(f"  <td>{read_status}</td>")

        return "<tr>\n" + "\n".join(row) + "\n</tr>"

    def sort_works_ids(self, ids: set[str]) -> list[str]:
        works_ids: list[str] = list(ids)

        def sorting_key(work_id: str) -> tuple[str, ...]:
            work: Work = self.works[work_id]
            if work.authors:
                author = self.authors[work.authors[0]].sorting_name.lower()
                fullname = self.authors[work.authors[0]].name.lower()
            else:
                author = "zz"
                fullname = "zzz"
            title = work.titles["fr"] if "fr" in work.titles else work.titles["en"]
            return (
                author,
                fullname,
                work.serie_id,
                work.serie_position,
                title,
            )

        works_ids.sort(key=lambda x: sorting_key(x))
        return works_ids

    def works_html_table(self, works_ids: set[str]) -> str:
        header: list[str] = [
            "<table>",
            "  <thead>",
            "    <tr>",
            "      <th>Titre</th>",
            "      <th>Titres alternatifs</th>",
            "      <th>Auteur·rice</th>",
            "      <th>Lu</th>",
            "      <th>Possédé</th>",
            "    </tr>",
            "  </thead>",
            "  <tbody>",
            "",
        ]
        sorted_works_ids: list[str] = self.sort_works_ids(works_ids)
        body: list[str] = [self.work_html_row(work_id) for work_id in sorted_works_ids]
        footer: list[str] = [
            "",
            "  </tbody>",
            "</table>",
        ]
        str_ = "\n".join(header) + textwrap.indent("\n".join(body), "    ") + "\n".join(footer)
        return str_

    def work_html_row(self, work_id: str) -> str:
        work: Work = self.works[work_id]
        row: list[str] = []

        primary_language: str = "fr" if "fr" in work.titles else "en"
        vo_marker: str = " VO" if primary_language == work.language else ""
        title: str = f"{work.titles[primary_language]} ({primary_language}{vo_marker})"

        alt_titles: list = []
        for language, alt_title in work.titles.items():
            if language != primary_language:
                vo_marker = " VO" if language == work.language else ""
                alt_titles.append(f"{alt_title} ({language}{vo_marker})")
        if not alt_titles:
            alt_titles.append("")

        rowspan: int = len(alt_titles)

        # Title
        row.append(f"<td rowspan={rowspan}>{title}</td>")
        # Others titles
        row.append(f"<td>{alt_titles[0]}</td>")
        # Authors
        authors: str = " / ".join([self.authors[author_id].name for author_id in work.authors])
        row.append(f"<td rowspan={rowspan}>{authors}</td>")
        # Read status
        read_status: str = "Lu" if work.read else "Pas Lu"
        row.append(f"<td rowspan={rowspan}>{read_status}</td>")
        # Possédé
        owned: str = "Possédé" if work.owned else "Non possédé"
        row.append(f"<td rowspan={rowspan}>{owned}</td>")

        for i in range(1, len(alt_titles)):
            row += [
                "</tr>",
                "<tr>",
                f"<td>{alt_titles[i]}</td>",
            ]

        return "<tr>\n" + textwrap.indent("\n".join(row), "  ") + "\n</tr>"

    def sort_authors_ids(self, ids: set[str], sorting: str) -> list[str]:
        assert sorting in ("name", "read", "owned_w", "owned_b")
        authors_ids: list[str] = list(ids)

        def sorting_key(author_id: str) -> tuple:
            author: Author = self.authors[author_id]
            if sorting == "name":
                return (author.sorting_name, author.name)
            elif sorting == "owned_w":
                return (-author.works_owned, author.sorting_name, author.name)
            elif sorting == "owned_b":
                return (-author.books_owned, author.sorting_name, author.name)
            elif sorting == "read":
                return (-author.works_read, author.sorting_name, author.name)

        authors_ids.sort(key=lambda x: sorting_key(x))
        return authors_ids

    def authors_html_table(self, authors_ids: set[str], sorting: str = "name") -> str:
        header: list[str] = [
            "<table>",
            "  <thead>",
            "    <tr>",
            "      <th>Auteur·rice</th>",
            "      <th>Nombre oeuvres lues</th>",
            "      <th>Nombre oeuvres possédées</th>",
            "      <th>Nombre livres possédés</th>",
            "    </tr>",
            "  </thead>",
            "  <tbody>",
            "",
        ]
        sorted_authors_ids: list[str] = self.sort_authors_ids(authors_ids, sorting)
        body: list[str] = [self.author_html_row(author_id) for author_id in sorted_authors_ids]
        footer: list[str] = [
            "",
            "  </tbody>",
            "</table>",
        ]
        str_ = "\n".join(header) + textwrap.indent("\n".join(body), "    ") + "\n".join(footer)
        return str_

    def author_html_row(self, author_id: str) -> str:
        author: Author = self.authors[author_id]
        row: list[str] = [
            f"<td>{author.name}</td>",
            f"<td>{author.works_read}</td>",
            f"<td>{author.works_owned}</td>",
            f"<td>{author.books_owned}</td>",
        ]
        return "<tr>\n" + textwrap.indent("\n".join(row), "  ") + "\n</tr>"


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
