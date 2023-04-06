import re

filename = "../possedes_ou_lus.md"

with open(filename, "r") as f:
    lines = f.readlines()
lines = [line[:-1] for line in lines]  # Get rid of \n

columns_pattern = re.compile(r"""^\|( [^|]*\|){8}$""")

# Check no trailing space and right number of columns
for i, line in enumerate(lines):
    if not (re.match(columns_pattern, line)):
        print(f"{i}: not right number of columns or wrong space pattern {line}")
