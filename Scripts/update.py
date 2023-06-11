#!/usr/bin/env python3

import os
import subprocess
import shutil

import check_file
import sort_by_authors
import stats_and_subsets

script_dir = os.path.abspath(os.path.dirname(__file__))
data_file = os.path.normpath(os.path.join(script_dir, "../possedes_ou_lus.md"))
sublist_path = os.path.normpath(os.path.join(script_dir, "../Sous_listes/"))
readme_path = os.path.normpath(os.path.join(script_dir, "../README.md"))

print(f"Loaded paths :\n"
      f"script directory: {script_dir}\n"
      f"data file : {data_file}\n"
      f"Sublists folder: {sublist_path}")

print("--- Checking File :")
res = check_file.check_file(data_file)
if res != 0:
    print(f"ERROR: please fix format of datafile: {data_file}")
    exit(1)

print("--- Sorting file by authors:")
sort_by_authors.sort_library(data_file, data_file)

print("--- Generating stats and subsets:")
stats_and_subsets.main(data_file, sublist_path, readme_path)

# shared the link to liste_ebook, need to keep it alive:
shutil.copy(sublist_path+"/ebook.md", sublist_path+"/liste_ebook.md")

print("--- Getting ready for git:")
cwd = os.getcwd()
os.chdir(os.path.normpath(os.path.join(script_dir, "../")))
print(f"Change of working directory, we are now here: {os.getcwd()}")

print("--- Staging files:")
print("Command: git stage possedes_ou_lus.md README.md Sous_listes/*")
subprocess.run(["git", "stage", "possedes_ou_lus.md", "README.md", "Sous_listes/*"])

print(f"--- Git commit:")
commit_message = input("Please input commit message (enter quit to quit): \n")
if commit_message == "quit" or commit_message == "exit":
    print("abort")
    exit()
while len(commit_message) < 4:
    commit_message = input("Commit message: ")
    if commit_message == "quit" or commit_message == "exit":
        print("abort")
        exit()

print(f'Command : git commit -m "{commit_message}"')
subprocess.run(["git", "commit", "-m", f'{commit_message}'])

print("--- Git Push:")
subprocess.run(["git", "push"])

os.chdir(cwd)
