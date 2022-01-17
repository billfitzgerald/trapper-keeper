import pandas as pd
import sys
import os
import shutil
import datetime
import tldextract
import csv
import json
import pyfiglet
import random 
from fnmatch import fnmatch
## custom functions
from utilities.helpers import (makedirs, clean_string, compress_text)


source_file = 'source/test_2.csv' # source of urls to collect - need two columns: url AND collection
text_dir = 'delivery' # base directory to hold text
url_data = 'url_data' # directory with information about urls that have already been archived

thank_you = pd.read_csv(source_file, delimiter=',', quotechar='"',)

makedirs(text_dir)
file_ext = "*.json"
all_files = []
all_urls = []
for path, subdirs, files in os.walk(url_data):
	for f in files:
		if fnmatch(f,file_ext):
			appdata = os.path.join(path,f)
			with open(appdata) as input:
				data = json.load(input)
				if data['current'] == "yes":
					url = data['url']
					if str(url)[-1:] == "/":
						url = str(url)[:-1]
					else:
						pass
					all_urls.append(url)
					all_files.append(data['filename_text'])

untracked_urls = []	
bad_urls = []			
for i, j in thank_you.iterrows():
	url = j.source_urls # url to retrieve
	if str(url)[-1:] == "/":
		url = str(url)[:-1]
	else:
		pass
	if url not in all_urls:
		untracked_url.append(url)
	elif url in all_urls:
		select_index = [i for i, value in enumerate(all_urls) if value == url]
		if len(select_index) == 1:
			file_path = all_files[select_index[0]]
			company = j.company
			company = clean_string(company)
			company = compress_text(company)
			outputdir = text_dir + "/" + company
			makedirs(outputdir)
			shutil.copy(file_path, outputdir)
		else:
			bad_urls.append(url)
	else:
		bad_urls.append(url)

print("\nThese URLs had some sort of issue. Review them:\n")
print(bad_urls)
print("\nThese URLs are not currently archived. Archive them, and then re-run this script:\n")
print(untracked_urls)

'''
requires a csv with at least two columns: source_urls and collection
read in list of urls from the csv
parse each url data file:
if current == yes and url == url then:
create output dir based on collection name
copy the text file into the new directory
'''
