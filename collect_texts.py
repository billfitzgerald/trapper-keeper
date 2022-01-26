import argparse
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

source_file = 'source/big_test.csv' # source of urls to collect - need two columns: url AND collection
text_dir = 'delivery' # base directory to hold text
url_data = 'url_data' # directory with information about urls that have already been archived

# process arguments
help_text = "Specify what gets collected and exported. '-c text' exports cleaned text; '-c html' exports text and html."
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--collect", dest="collect", default="text", help=help_text)
args = parser.parse_args()
whattodo = args.collect

if whattodo == "text":
	pass
elif whattodo == "html":
	pass
else:
	sys.exit(help_text)

# define dataframes
thank_you = pd.read_csv(source_file, delimiter=',', quotechar='"',)
df_collect = pd.DataFrame(columns=['url', 'accessed_on', 'current', 'filename_full', 'full_count', 'filename_text', 'text_count', 'text_hash', 'filename_snippet', 'first', 'last', 'middle'])

print("Getting information about archived urls. \n")
makedirs(text_dir)
all_urls = []
file_ext = "*.json"
for path, subdirs, files in os.walk(url_data):
	for f in files:
		if fnmatch(f,file_ext):
			appdata = os.path.join(path,f)
			with open(appdata) as input:
				data = json.load(input)
				if data['current'] == "yes":
					try:
						url = data['url']
						if url not in all_urls:
							all_urls.append(url)
					except:
						url = ""
					try:
						accessed_on = data['accessed_on']
					except:
						accessed_on = ""
					try:
						current = data['current']
					except:
						current = ""
					try:
						filename_full = data['filename_full']
					except:
						filename_full = ""
					try:
						full_count = data['full_count']
					except:
						full_count = ""
					try:
						filename_text = data['filename_text']
					except:
						filename_text = ""
					try:
						text_count = data['text_count']
					except:
						text_count = ""
					try:
						text_hash = data['text_hash']
					except:
						text_hash = ""
					try:
						filename_snippet = data['filename_snippet']
					except:
						filename_snippet = ""
					try:
						first = data['first']
					except:
						first = ""
					try:
						last = data['last']
					except:
						last = ""
					try:
						middle = data['middle']
					except:
						middle = ""	
					df_collect.loc[df_collect.shape[0]] = [url, accessed_on, current, filename_full, full_count, filename_text, text_count, text_hash, filename_snippet, first, last, middle]
				else:
					pass

untracked_urls = []	
bad_urls = []

print("Preparing files for export.\n")
for i, j in thank_you.iterrows():
	bad_text = ""
	url = j.source_urls # url to retrieve
	print(f" * finding files related to {url}\n")
	if str(url)[-1:] == "/":
		url = str(url)[:-1]
	else:
		pass
	if url not in all_urls:
		untracked_urls.append(url)
	elif url in all_urls:
		urlinfo = df_collect[(df_collect['url'] == url)]
		collection = j.collection
		collection = clean_string(collection)
		collection = compress_text(collection)
		try:
			text_filepath = urlinfo['filename_text'].iloc[0]
			text_outputdir = text_dir + "/" + collection + "/text"
			makedirs(text_outputdir)
			shutil.copy(text_filepath, text_outputdir)
		except:
			bad_text = f'Text copy failed for {url}'
			bad_urls.append(bad_text)

		if whattodo == 'html':
			try:
				snippet_filepath = urlinfo['filename_snippet'].iloc[0]
				if len(snippet_filepath) > 3:
					snip_outputdir = text_dir + "/" + collection + "/snippet"
					makedirs(snip_outputdir)
					shutil.copy(snippet_filepath, snip_outputdir)
				else:
					pass
			except:
				bad_text = f'Snippet copy failed for {url}'
				bad_urls.append(bad_text)

			try:
				file_filepath = urlinfo['filename_full'].iloc[0]
				file_outputdir = text_dir + "/" + collection + "/full"
				makedirs(file_outputdir)
				shutil.copy(file_filepath, file_outputdir)
			except:
				bad_text = f'Source file copy failed for {url}'
				bad_urls.append(bad_text)
		else:
			pass

if len(bad_urls) > 0:
	print("\nThese URLs had some sort of issue. Review them:\n")
	for b in bad_urls:
		print(f' * {b}')

if len(untracked_urls) > 0:
	print("\nThese URLs are not currently archived. Archive them, and then re-run this script:\n")
	for u in untracked_urls:
		print(f' * {u}')

print(f'\n* * *\nExport complete! Check the /{text_dir} directory for the files.\n* * *\n')