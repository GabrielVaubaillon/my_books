import re
import sys
import os
import argparse

script_dir = os.path.abspath(os.path.dirname(__file__))
file = os.path.join(script_dir, "../possedes_ou_lus.md")

parser = argparse.ArgumentParser(
        prog='md_to_csv',
        description="Convert the md table to a csv stream")

parser.add_argument('-o', '--output-file',
                    help="csv file created, stdout by default",
                    default="stdout")
parser.add_argument('-i','--input-file',
                    help="markdown table file, my_books/possedes_ou_lus.md by default",
                    default=file)

args = parser.parse_args()

print(args)

file_in = args.input_file
file_out = args.output_file

if args.input_file == "stdin":
    file_in = sys.stdin
else:
    file_in = open(args.input_file, 'r')

if args.output_file == "stdout":
    file_out = sys.stdout
else:
    file_out = open(args.output_file, 'w')


try:
    for i, line in enumerate(file_in.readlines()):
        if i == 1:
            continue
        str_out = line[1:-2]
        str_out = re.sub(r" *\| *", ";", str_out)
        file_out.write(str_out+"\n")
    file_out.flush()
except BrokenPipeError:
    # Python flushes standard streams on exit; redirect remaining output
    # to devnull to avoid another BrokenPipeError at shutdown
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stdout.fileno())
    sys.exit(1)  # Python exits with error code 1 on EPIPE
    
file_in.close()
file_out.close()
