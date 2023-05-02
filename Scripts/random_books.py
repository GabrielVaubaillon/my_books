#!/usr/bin/env python3
import os
import random
import argparse
import data_management as dm


def verbose_print(string):
    if verbose:
        print(string)


parser = argparse.ArgumentParser(
    prog='random_book',
    description="Extract n randoms books")

parser.add_argument('-v', '--verbose',
                    help="Print more info during execution",
                    action="store_true")

parser.add_argument('-n', '--books-number',
                    help="The number of random book to display",
                    type=int,
                    default=5)

parser.add_argument('-a', '--include-all',
                    help="include all books, not just not-read",
                    action="store_true")

args = parser.parse_args()
verbose = args.verbose
n_books = args.books_number
include_all = args.include_all

script_dir = os.path.abspath(os.path.dirname(__file__))
data_file = os.path.join(script_dir, "../possedes_ou_lus.md")

verbose_print(f"Loadings books from file ({data_file})")
with open(data_file, "r") as f:
    library = dm.list_from_md_file(f)

verbose_print("Sorting books")
random.shuffle(library)

if not include_all:
    library = [book for book in library if book.read != "Lu"]

for i in range(min(n_books, len(library))):
    print(library[i].to_str(";  "))
