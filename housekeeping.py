import sys
import re
import os
import shutil
import json
from fnmatch import fnmatch
from utilities.helpers import (makedirs)

base = "archive" # location of all collected docs
url_data = "url_data" # location of json files about tracked urls
orphans = "manual_review" # location where untracked files are moved for review

makedirs(orphans)

# get list of all required files
file_ext = "*.json"
required_files = []
for path, subdirs, files in os.walk(url_data):
	for f in files:
		print("Processing " + f)
		if fnmatch(f,file_ext):
			appdata = os.path.join(path,f)
			with open(appdata) as input:
				data = json.load(input)
				try:
					required_files.append(data['filename_full'])
				except:
					pass
				try:
					required_files.append(data['filename_text'])
				except:
					pass
				try:
					required_files.append(data['filename_snippet'])
				except:
					pass

# get list of all files in archive directory
file_ext = "*.*"
move_files = []
for path, subdirs, files in os.walk(base):
	for f in files:
		if fnmatch(f,file_ext):
			filedata = os.path.join(path,f)
			if filedata not in required_files:
				move_files.append(filedata)
				shutil.move(filedata, orphans)
			
print("\nThese files are actively tracked with url data:\n")
for r in required_files:
	print(f" * {r}")

print("\n ********* \n\nThe following files have been moved:\n")

if len(move_files) == 0:
	print(" * No files needed to be moved.")
else:
	for m in move_files:
		print(f" * {m}")
