#!/usr/bin/env python3
import os
import random
import argparse
import data_management as dm

def verbose_print(string):
    if args.verbose:
        print(string)


parser = argparse.ArgumentParser(
    prog='random_book',
    description="Extract n randoms books")

parser.add_argument('-v', '--verbose',
                    help="Print more info during execution",
                    action="store_true")

parser.add_argument('-n', '--number-books',
                    help="The number of random book to display",
                    type=int,
                    default=5)

parser.add_argument('-a', '--all',
                    help="Override -n, show all (valid, see others parameters) books in random order",
                    action="store_true")

parser.add_argument('-r', '--include-read',
                    help="include all books, not just not-read",
                    action="store_true")

parser.add_argument('-i', '--in-location',
                    help="Only include books from these locations",
                    choices=dm.LOCATIONS.keys(),
                    nargs='+')

parser.add_argument('-e', '--exclude-location',
                    help="Only include books from these locations",
                    choices=dm.LOCATIONS.keys(),
                    nargs='+')

parser.add_argument('-m', '--markdown',
                    help="Print books in markdown table",
                    action='store_true')

args = parser.parse_args()

script_dir = os.path.abspath(os.path.dirname(__file__))
data_file = os.path.normpath(os.path.join(script_dir, "../possedes_ou_lus.md"))

verbose_print(f"Loadings books from file ({data_file})")
with open(data_file, "r") as f:
    library = dm.list_from_md_file(f)

verbose_print(f"Loadings books from file ({data_file})")
if not args.include_read:
    library = [book for book in library if book.read != "Lu"]

# Keep included locations
if args.in_location:
    new_library = []
    for location in args.in_location:
        for i, book in enumerate(library):
            if book.situation in dm.LOCATIONS[location]:
                new_library.append(book)
                library.pop(i)
    library = new_library

if args.exclude_location:
    for location in args.exclude_location:
        library = [book for book in library if not book.situation.lower().startswith(location)]

verbose_print("Shuffling books")
random.shuffle(library)

if not args.all:
    n_show = min(args.number_books, len(library))
else:
    n_show = len(library)

if not args.markdown:
    for i in range(n_show):
        print(library[i].to_str(";  "))
else:
    print(dm.HEADER)
    for i in range(min(n_show, len(library))):
        print(library[i].to_str())
    print()
