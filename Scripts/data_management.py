import re

HEADER = ("| Titre | Auteur | Langue | ISBN | Possédé | Lu | Situation | Notes |\n"
          "| --- | --- | --- | --- | --- | --- | --- | --- |\n")


class Book:
    """Class representing a book in this repo"""

    def __init__(self,
                 title,
                 author,
                 language,
                 isbn,
                 owned,
                 read,
                 situation,
                 notes):
        self.title = title
        self.author = author
        self.author_lastname = Book.extract_author_lastname(author)
        self.language = language
        self.isbn = isbn
        self.owned = owned
        self.read = read
        self.situation = situation
        self.notes = notes

    @classmethod
    def from_md_line(cls, line):
        string = line[1:-2]
        string = re.sub(r" *\| *", ";", string)
        values = string.split(";")
        return cls(values[0], values[1], values[2], values[3], values[4], values[5], values[6], values[7])

    def to_str(self, sep=" | "):
        """Return a string of the book, sep=";" or " | " for normal operations"""
        book_str = (self.title + sep
                    + self.author + sep
                    + self.language + sep
                    + self.isbn + sep
                    + self.owned + sep
                    + self.read + sep
                    + self.situation + sep
                    + self.notes)
        if sep == " | ":
            book_str = "| " + book_str + " |"
        book_str = re.sub(r"  ", r" ", book_str)
        return book_str

    def __lt__(self, other):
        if self.author_lastname == other.author_lastname:
            return no_accents_lower(self.title) < no_accents_lower(other.title)
        elif self.author_lastname == '':
            return False
        else:
            return self.author_lastname < other.author_lastname

    def __gt__(self, other):
        # I choose to not write equality for Book
        return not self.__lt__(other)

    def __str__(self):
        return self.to_str(sep=";")

    @staticmethod
    def extract_author_lastname(author):
        author = author.strip(" ")
        if author == "":
            return ""
        # if two authors, we keep the first
        if "&" in author:
            author = author.split("&")[0]
        # Get rid of spaces around name
        author = author.strip(" ")
        # Split name and lastname
        author = author.split(" ")
        # get rid of seniors
        while no_accents_lower(author[-1]) in ["fils", "pere", "aine", "junior", "senior"]:
            author.pop(-1)
        lastname = author[-1]
        return lastname


def no_accents_lower(string):
    new_string = ""
    for c in string.lower():
        if c in "éèêë":
            new_string += 'e'
        elif c in "â":
            new_string += 'a'
        elif c in "ç":
            new_string += 'c'
        elif c in "ïî":
            new_string += 'i'
        elif c in "ôö":
            new_string += 'o'
        elif c in 'ù':
            new_string += 'u'
        else:
            new_string += c
    return new_string


def list_from_md_file(file_in):
    library = []

    # Without header :
    file_in.readline()
    file_in.readline()
    for line in file_in.readlines():
        library.append(Book.from_md_line(line))
    return library
