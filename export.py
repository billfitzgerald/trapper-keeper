import pandas as pd
import sys
import os
import argparse
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

export_dir = "export"
url_data = "url_data"

# process arguments
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--export", dest="exp", default="current", help="Specify 'current' or 'all'.")
args = parser.parse_args()
whattodo = args.exp

if whattodo == "current":
	pass
elif whattodo == "all":
	pass	
else:
	sys.exit("Specify the type of export. '-e current' exports the latest urls; '-e all' exports all records.")

d = datetime.datetime.today()
year = d.strftime("%Y")
month = d.strftime("%m")
day = d.strftime("%d")
date_filename = year + "_" + month + "_" + day

# define dataframes
df_export = pd.DataFrame(columns=['url', 'initial_save', 'accessed_on', 'pdf', 'current', 'filename_full', 'full_count', 'filename_text', 'text_count', 'text_hash', 'filename_snippet', 'first', 'last', 'middle'])

## If we're running an export let's get it done and get out
makedirs(export_dir)
file_ext = "*.json"
for path, subdirs, files in os.walk(url_data):
	for f in files:
		if fnmatch(f,file_ext):
			appdata = os.path.join(path,f)
			with open(appdata) as input:
				data = json.load(input)
				try:
					url = data['url']
				except:
					url = ""
				try:
					initial_save = data['first_saved']
				except:
					initial_save = ""
				try:
					accessed_on = data['accessed_on']
				except:
					accessed_on = ""
				try:
					pdf = data['run_pdf']
				except:
					pdf = ""
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
				export_obj = pd.Series([url, initial_save, accessed_on, pdf, current, filename_full, full_count, filename_text, text_count, text_hash, filename_snippet, first, last, middle], index=df_export.columns)
				df_export = df_export.append(export_obj, ignore_index=True)

if whattodo == "current":
	df_export = df_export[(df_export['current'] == "yes")]
else:
	pass

export_out = export_dir + "/" + date_filename + "_" + whattodo + ".csv"
df_export.to_csv(export_out, encoding='utf-8', index=False)
print(f"Export written to {export_out}")