import difflib
from difflib import HtmlDiff
import pandas as pd
import sys
#import re
import os
#import datetime
from datetime import datetime
import tldextract
import csv
import json
import webbrowser
from fnmatch import fnmatch
import random
import tldextract
from utilities.helpers import (makedirs)

# define source csv for urls to check for diffs
# must have four columns: source_urls yyyy mm dd
source_file = "source/diff_check_base.csv"

# path to json files about stored urls
url_data = "url_data"
diff_dir = "diffs"

d = datetime.now()
year = d.strftime("%Y")
month = d.strftime("%m")
day = d.strftime("%d")
date_filename = year + "_" + month + "_" + day

#define dataframes
df_diffs = pd.DataFrame(columns=['path', 'accessed_date', 'text_path'])

###############
## Functions ##
###############

def htmldiff(string1, string2):

	try:
		txt1 = string1.decode('utf-8').splitlines()
	except AttributeError:
		txt1 = string1.splitlines()

	try:
		txt2 = string2.decode('utf-8').splitlines()
	except AttributeError:
		txt2 = string2.splitlines()

	diff = HtmlDiff(tabsize=4, wrapcolumn=80)

	diff._styles = diff._styles + """

		table.diff {
			margin: 30px;
			padding:10px;
			background-color: gold;
			box-shadow: 5px 5px 5px #aaa;
		}

		td {
			background-color: white;
		}
		td.diff_header {
			padding:8px;
		}
		.diff_next {
			padding:10px;
		}
		th.newversion {
			color: red;
		}
		th.oldversion {
			color: red;
		}
		"""

	result = diff.make_file(txt1, txt2, context=True, numlines=20)

	return result

## Get to work

makedirs(diff_dir)
# to start get all urls and filenames from url json files
file_ext = "*.json"
all_paths = []
all_urls = []
for path, subdirs, files in os.walk(url_data):
	for f in files:
		print("Reading " + f)
		if fnmatch(f,file_ext):
			appdata = os.path.join(path,f)
			all_paths.append(appdata)
			with open(appdata) as input:
				data = json.load(input)
				all_urls.append(data['url'])

print(f"\n*  *  *  *\nReading archive data complete. Moving on.\nChecking for diffs\n*  *  *  *\n")

# import csv file with at least four columns: url and yyyy mm dd
thank_you = pd.read_csv(source_file, delimiter=',', quotechar='"',) 
count = 0
for i, j in thank_you.iterrows():
	df_diffs = df_diffs[0:0]
	output_type = ""
	url = j.source_urls # url to check 
	if str(url)[-1:] == "/":
		url = str(url)[:-1]
	else:
		pass
	year = j.yyyy
	month = j.mm
	day = j.dd
	check_date = datetime.strptime(f'{year}-{month}-{day}', '%Y-%m-%d')
	somenum = random.randint(1000,9999)
	temp_netloc = tldextract.extract(url) 
	netloc = temp_netloc.domain + '_' + temp_netloc.suffix
	select_index = [i for i, value in enumerate(all_urls) if value == url]
	if len(select_index) <=1:
		print(f" * NO DIFF! For {url}, we have {len(select_index)} entries, and therefore nothing to compare!\n")
	elif len(select_index) > 1:
		for si in select_index:				
			file_path = all_paths[si]
			with open(file_path) as input:
				# open each file, and store the filepath, current, accessed date, and path to text file
				data = json.load(input)
				if data['current'] == "no":
					path = file_path
					accessed_date = data['accessed_on']
					accessed_date = accessed_date[:10]
					accessed_date = datetime.strptime(f'{accessed_date}', '%Y-%m-%d')
					text_path = data['filename_text']
					diff_obj = pd.Series([path, accessed_date, text_path], index=df_diffs.columns)
					df_diffs = df_diffs.append(diff_obj, ignore_index=True)
				elif data['current'] == "yes":
					current_path = data['filename_text']
					current_date = data['accessed_on']
					current_date = str(current_date)[:10]
					with open(current_path, 'r') as f:
						current = f.read()
				else:
					pass
		# if there are two or more versions of a url, get the *oldest* version 
		# that is after the cutoff date specified in the csv
		df_diffs = df_diffs[(df_diffs['accessed_date'] > check_date)]
		df_diffs.sort_values(by=['accessed_date'], inplace=True, ascending=True)
		old_version = df_diffs['text_path'].iloc[0]
		old_date = df_diffs['accessed_date'].iloc[0]
		old_date = str(old_date)[:10]

		with open(old_version, 'r') as o:
			old = o.read()

		# run a diff on the oldest version after the cutoff date and the current version
		print(f" * Running a diff on {url}\n")
		html = htmldiff(old, current)
		count += 1
		# this html cleanup is janky af
		# but it works 
		# TODO research better/cleaner options with difflib output
		title = f"<title>Diff on {url}"
		html = html.replace('<title>', title)
		explanation = f'<h2>Policy Updates</h2><p>This page shows differences between two versions of the content from {url}.</p>'
		explanation = explanation + f'<p>The <b>most recent version is on the right</b>; it was accessed on {current_date}</p>'
		explanation = explanation + f'<p>The <b>older version</b> is on the left; it was accessed on {old_date}</p>'
		explanation = f'<body>{explanation}'
		html = html.replace('<body>', explanation)
		table_headers = f'<tbody><tr><th></th><th></th><th class="oldversion">Old Version from {old_date}</th><th></th><th></th><th class="newversion">Current Version from {current_date}</th> </tr>'
		html = html.replace('<tbody>', table_headers)

		name_out = f"{diff_dir}/{netloc}_{date_filename}_{somenum}.html"

		with open(name_out, 'w') as fh:
			fh.write(html)

		# open in web browser
		webbrowser.open(name_out)

	else:
		print(f"\n* * * *\nCheck data related to {url} - something is awry.\n* * * *\n")

