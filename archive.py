import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from configparser import ConfigParser
from bs4 import BeautifulSoup
import pandas as pd
import sys
import re
import os
import datetime
import tldextract
import csv
import json
import pyfiglet
import requests
import random
from collections import OrderedDict
from fnmatch import fnmatch
from io import StringIO
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
import hashlib
import time
import platform
## custom functions
from utilities.helpers import (makedirs, prep_request, write_csv, clean_string, text_excerpt, compress_text, pointcalc, write_file, clean_json, headers_all, rando_url)

operating_system = platform.system()
operating_system_release = platform.release()
if operating_system == "Linux":
	import ocrmypdf
else:
	pass

# process arguments
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--process", dest="check", default="csv", help="Specify what gets processed. '-p update' checks existing urls; '-p csv' reads urls from a csv.")
args = parser.parse_args()
whattodo = args.check

if whattodo == "csv":
	# specify source file
	# file should be a csv with 4 columns: 'source_urls','opening', 'middle', 'closing'
	# 'opening' is the first few words where the relevant text begins
	# 'closing' is the final words of the relevant text
	# 'middle'  is a snippet in the middle of the relevant text
	source_file = 'source/new_docs_2.csv' 
elif whattodo == "update":
	pass
else:
	sys.exit("Specify source of urls. '-p update' checks existing urls; '-p csv' reads urls from a csv")


character = 100 # set minimum character count for text
cutoff = 6 # scoring threshold - 7 is currently max

count = 0
bad_urls = []
url_updated = []

# specify profile with enabled browser extensions
'''
testing_profile = FirefoxProfile("/home/username/.mozilla/firefox/profile_name")
binary = FirefoxBinary("/usr/bin/firefox")
driver = webdriver.Firefox(firefox_profile=testing_profile, firefox_binary=binary)
ext_dir = '/home/username/.mozilla/firefox/profile_name/extensions/'
extensions = [
	'uBlock0@raymondhill.net.xpi',
	]
for e in extensions:
   driver.install_addon(ext_dir + e, temporary=True)
'''
#uncomment to use standard gecko driver
profile = webdriver.FirefoxProfile()
profile.set_preference("browser.cache.disk.enable", False)
profile.set_preference("browser.cache.memory.enable", False)
profile.set_preference("browser.cache.offline.enable", False)
profile.set_preference("network.http.use-cache", False) 
driver = webdriver.Firefox(profile)

# Create output directories
base = 'archive' # use for archiving policies
full_html = "full"
snippet_html = "snippet"
clean_text_dir = "text"
supporting_files = "files"
media = "media"
url_data = "url_data"
d = datetime.datetime.today()
year = d.strftime("%Y")
month = d.strftime("%m")
day = d.strftime("%d")
date_filename = year + "_" + month + "_" + day

#######################

#define dataframes
df_language = pd.DataFrame(columns=['check', 'text_len', 'text', 'mu_len', 'markup_snippet', 'full_page_len'])
thank_you = pd.DataFrame(columns=['source_url', 'pdf', 'opening', 'middle', 'closing'])

print(f'OS appears to be {operating_system}, release version {operating_system_release}\n')

#######################
## Let's get started ##
#######################
# get key data from existing url archives
makedirs(url_data)
makedirs(media)
file_ext = "*.json"
all_files = []
all_hash = []
all_urls = []
for path, subdirs, files in os.walk(url_data):
	for f in files:
		print("Processing " + f)
		if fnmatch(f,file_ext):
			appdata = os.path.join(path,f)
			all_files.append(f)
			with open(appdata) as input:
				data = json.load(input)
				all_urls.append(data['url'])
				all_hash.append(data['text_hash'])
				if data['current'] == "yes" and whattodo == "update":
					url = data['url']
					try:
						pdf = data['run_pdf']
					except:
						pdf = ""
					try:
						opening = data['first']
					except:
						opening = ""
					try:
						middle = data['middle']
					except:
						middle = ""
					try:
						closing = data['last']
					except:
						closing = ""
					ty_obj = pd.Series([url, pdf, opening, middle, closing], index=thank_you.columns)
					thank_you = thank_you.append(ty_obj, ignore_index=True)

if whattodo == "csv":
	thank_you = pd.read_csv(source_file, delimiter=',', quotechar='"',) 
else:
	pass

processed_url = []

thank_you = thank_you.sample(frac=1)
#thank_you.to_csv('thank_you_shuffle.csv', encoding='utf-8', index=False)
#sys.exit("We out!")
old_domain = "xyz.com"
for i, j in thank_you.iterrows():
	output_type = ""
	url = j.source_url # url to retrieve
	processed_url.append(url)
	if str(url)[-1:] == "/":
		url = str(url)[:-1]
	else:
		pass
	try:
		pdf_proc = j.pdf
	except:
		pdf_proc = ""
	print(f"Processing {url}\n")
	if url not in all_urls:
		new_url = "yes"
	elif url in all_urls:
		new_url = "no"
	else:
		bad_urls.append(url)
	temp_netloc = tldextract.extract(url) 
	netloc = temp_netloc.domain + '_' + temp_netloc.suffix
	new_domain = temp_netloc.domain + '.' + temp_netloc.suffix
	if new_domain == old_domain:
		print(f'Slowing down due to a domain match!\n{new_domain} is the same as {old_domain}.\n')
		rando = rando_url()
		driver.get(rando)
		rr_l = [8,9,10,11,12,14,15,16]
		rr = random.choice(rr_l)
		print(f"sleeping for {rr} seconds")
		time.sleep(rr)
		print("waking up - let's get to work!")
	else:
		pass
	old_domain = new_domain
	url_service = url_data + "/" + netloc
	storage_dir = netloc
	sd_full = f"{base}/{storage_dir}/{full_html}"
	sd_snippet = f"{base}/{storage_dir}/{snippet_html}"
	sd_text = f"{base}/{storage_dir}/{clean_text_dir}"
	sd_files = f"{base}/{storage_dir}/{supporting_files}"
	somenum = random.randint(1000,9999)
	filename = url.split('/')[-1]
	if len(filename) < 2:
		filename = url.split('/')[-2]
	else:
		pass
	fn = date_filename + "_" + str(somenum) + "_" + filename
	makedirs(sd_full)
	makedirs(sd_snippet)
	makedirs(sd_text)
	makedirs(sd_files)
	makedirs(url_service)
	## trap for filename extensions
	if str(url)[-4:] == ".pdf" or pdf_proc == "y":
		try:			
			r = prep_request()
			response = r.get(url, timeout=90) 
			file_output = sd_text + "/" + fn
			if file_output[-4:] != ".pdf":
				file_output = file_output + ".pdf"
			else:
				pass
			with open(file_output,'wb') as output_file:
				output_file.write(response.content)
			output_type = "pdf"
		except:
			output_type = "none"
			bad_text = f'PDF could not be accessed. Review {url}'
			bad_urls.append(bad_text)
		if output_type == "pdf":
			try:
				third_try = "no"
				text_output = sd_text + "/" + fn
				text_output = text_output.replace(".pdf", ".txt")
				## check starts here
				if operating_system == "Linux":
					pdf_out = sd_text + "/COPY_" + fn 
					if pdf_out[-4:] != ".pdf":
						pdf_out = pdf_out + ".pdf"
					else:
						pass
					try: 
						ocrmypdf.ocr(file_output, pdf_out, deskew=True, sidecar=text_output, remove_background=True, pdfa_image_compression="jpeg")
					except:
						try:
							ocrmypdf.ocr(file_output, pdf_out, deskew=True, sidecar=text_output, remove_background=True, pdfa_image_compression="jpeg", force_ocr=True)
						except:
							third_try = "yes"
							try:
								output_string = StringIO()
								with open(file_output, 'rb') as in_file:
									parser = PDFParser(in_file)
									doc = PDFDocument(parser)
									pdf_meta = doc.info
									print(pdf_meta)
									rsrcmgr = PDFResourceManager()
									device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
									interpreter = PDFPageInterpreter(rsrcmgr, device)
									for page in PDFPage.create_pages(doc):
										interpreter.process_page(page)
								pdf_extract = output_string.getvalue()
								body = pdf_extract
								body = body.replace('  ', ' ')
								body = body.replace('^p', ' ')
								body = body.replace('\r\n', ' ')
								body = body.replace('\r', ' ')
								body = body.replace('\n\n\n', '\n\n')
								#body = body.replace('\n\n', '\n')
								body = body.replace('', '')
							except:
								third_try = "maybe"
								output_type = "none"
								print(f"Check {fn} because the scan didn't work.")
								bad_urls.append(url + " pdf convert")
					
					if third_try == "no":
						body = ""
						with open (text_output, 'r') as to_be_cleaned:
							for line in to_be_cleaned:
								if len(line) > 20:
									line = line.rstrip('\r')
									line = line.rstrip('\n')
									body = body + line
								else:
									body = body + "\n" + line
							
							body = body.replace('\n\n\n', '\n\n')
							body = body.replace('', '')
					else:
						pass

				elif operating_system == "Darwin":
					output_string = StringIO()
					with open(file_output, 'rb') as in_file:
						parser = PDFParser(in_file)
						doc = PDFDocument(parser)
						pdf_meta = doc.info
						print(pdf_meta)
						rsrcmgr = PDFResourceManager()
						device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
						interpreter = PDFPageInterpreter(rsrcmgr, device)
						for page in PDFPage.create_pages(doc):
							interpreter.process_page(page)
					pdf_extract = output_string.getvalue()
					body = pdf_extract
					body = body.replace('  ', ' ')
					body = body.replace('^p', ' ')
					body = body.replace('\r\n', ' ')
					body = body.replace('\r', ' ')
					body = body.replace('\n\n\n', '\n\n')
					#body = body.replace('\n\n', '\n')
					body = body.replace('', '')
				
				else:
					print("Only Linux and OSX are supported for PDF conversion.")
				# check ends here

				if len(body) > 1:
					flatten = compress_text(body)
					hash_obj = hashlib.md5(flatten.encode())
					th = hash_obj.hexdigest()
					with open (text_output, 'w') as to_be_cleaned:
						to_be_cleaned.write(body)
				else:
					pass

			except:
				bad_text = f'PDF could be downloaded, but not processed. Check {url}'
				bad_urls.append(bad_text)
	# trap for word files
	elif str(url)[-4:] == ".doc":
		output_type = "word"
		r = prep_request()
		response = r.get(url) 
		file_output = sd_files + "/" + fn
		with open(file_output,'wb') as output_file:
			output_file.write(response.content)
	elif str(url)[-5:] == ".docx":
		output_type = "word"
		r = prep_request()
		response = r.get(url) 
		file_output = sd_files + "/" + fn
		with open(file_output,'wb') as output_file:
			output_file.write(response.content)
	# trap for text files; drop in text directory
	elif str(url)[-4:] == ".txt":
		output_type = "text"
		r = prep_request()
		response = r.get(url) 
		file_output = sd_text + "/" + fn
		with open(file_output,'wb') as output_file:
			output_file.write(response.content)

	else:
		output_type = "web_page"
		df_language = df_language[0:0]
		opening_text = j.opening
		middle_text = j.middle
		closing_text = j.closing
		count += 1
		driver.delete_all_cookies()
		driver.get(url)
		current_url = driver.current_url
	#Selenium hands the page source to Beautiful Soup
		soup=BeautifulSoup(driver.page_source, 'lxml')
		fo_full = sd_full + "/full_" + fn + ".html"
		with open(fo_full,'w') as output_file:
			output_file.write(str(soup.prettify()))
		full_page_markup = len(str(soup))
		try:
			page_title = soup.title.get_text(strip=True) # pull title from the page
		except:
			try:
				# this is largely placeholder - there are better things we can try here
				driver.close()
				driver = webdriver.Firefox(profile)
				driver.delete_all_cookies()
				rando = rando_url()
				driver.get(rando)
				print(f'Retrying {url}\n')
				time.sleep(15)
				driver.get(url)
				current_url = driver.current_url
				soup=BeautifulSoup(driver.page_source, 'lxml')
				page_title = soup.title.get_text(strip=True)
			except:
				bad_message = f"page_title check failed for {url} - probably due to a captcha check"
				bad_urls.append(bad_message)
				soup = BeautifulSoup('<head></head>', 'lxml')
				page_title = "page title went bad"
		body = soup.body
		try:
			full_text_count = len(body)
			bodytags = {tag.name for tag in body.find_all()}
		except:
			full_text_count = 0
			bodytags = []
		if len(bodytags) > 0:
			for bt in bodytags:
				for i in body.find_all(bt):
					text = i.get_text().strip()
					text = text.replace('\n\n\n', '\n').replace('\n\n', '\n')
					closing = compress_text(closing_text)
					opening = compress_text(opening_text)
					middle = compress_text(middle_text)
					check = pointcalc(text, closing, opening, middle,character)
					id_str = ""
					class_str = ""
					if check > cutoff:
						## write to dataframe: check, text_len, text, mu_len, i, full_page_length
						text_len = len(text)
						mu_len = len(str(i))
						df_language.loc[df_language.shape[0]] = [check, text_len, text, mu_len, i, full_page_markup]
						if i.has_attr("class"):
							if len(i['class']) != 0:
								cstr = i['class']
								class_str = f"Class: {cstr};"
							else:
								pass
						else:
							pass
						if i.has_attr("id"):
							if len(i['id']) != 0:
								idstr = i['id']
								id_str = f"Id: {idstr}"
							else:
								pass
						else:
							pass	
						
					else:
						pass
			try:
				text_len_list = df_language['text_len'].to_list()
				mu_len_list = df_language['mu_len'].to_list()
				text_len_small = min(text_len_list)
				mu_len_small = min(mu_len_list)
				df_clean = df_language[(df_language['text_len'] == text_len_small) & (df_language['mu_len'] == mu_len_small)]
				link_list = []
				img_list = []
				if df_clean.shape[0] > 0:
					text = df_clean['text'].iloc[0]
					markup = df_clean['markup_snippet'].iloc[0]				
				elif df_clean.shape[0] == 0:
					mu_len_list.sort()
					mu_len_small = mu_len_list[1]
					df_clean = df_language[(df_language['text_len'] == text_len_small) & (df_language['mu_len'] == mu_len_small)]
					text = df_clean['text'].iloc[0]
					markup = df_clean['markup_snippet'].iloc[0]
				else:
					bad_text = f"There is an issue with text from {url}"
					bad_urls.append(bad_text)

				# drop cruft from beginning and end
				try:
					text_hold = text.rsplit(closing_text,1)
					text = text_hold[0] + closing_text
				except:
					try: 
						ct = closing_text[-10:]
						text_hold = text.rsplit(ct,1)
						text = text_hold[0] + ct
					except:
						try: 
							ct = closing_text[-5:]
							text_hold = text.rsplit(ct,1)
							text = text_hold[0] + closing_text
						except:
							print(ct)
							print(closing_text)
							print("Examine the closing text")
				try:
					text_hold = text.split(opening_text,1)
					text = opening_text + text_hold[1]
				except:
					try: 
						ot = opening_text[:15]
						ot = ot.strip()
						text_hold = text.split(ot,1)
						text = ot + text_hold[1]
					except:
						try: 
							ot = opening_text[:8]
							ot = ot.strip()
							text_hold = text.split(ot,1)
							text = ot + text_hold[1]
						except:
							print(ot)
							print(opening_text)
							print("Examine the opening text")

				clean_text_length = len(text)
				flatten = compress_text(text)
				hash_obj = hashlib.md5(flatten.encode())
				th = hash_obj.hexdigest()
				text_hash = f'"text_hash":"{th}",'

				for link in markup.find_all('a', href=True):
					l = link['href']
					if l not in link_list:
						link_list.append(l)
				for image in markup.find_all('img', src=True):
					i = image['src']
					if i not in img_list:
						img_list.append(i)

				ll_text = f"\n\n---\nLinks in the page:\n\n"
				link_list.sort()
				for ll in link_list:
					ll_text = ll_text + f" * {ll}\n"
				ll_text = ll_text + "\n"

				img_text = f"---\nImages in the page:\n\n"
				img_list.sort()
				for img in img_list:
					img_text = img_text + f" * {img}\n"
					try:
						r = prep_request()
						response = r.get(img)
						iname = img.split('/')[-1] 
						image_output = date_filename + "_" + iname
						file_output = media + "/" + image_output
						with open(file_output,'wb') as output_file:
							output_file.write(response.content)
					except:
						bad_urls.append(img)

				img_text = img_text + "\n"

				text = text + ll_text + img_text
				txt_count = len(text)

				fo_text = sd_text + "/text_" + fn + ".txt"
				with open(fo_text,'w') as output_file:
					output_file.write(text)

				fo_snip = sd_snippet + "/snippet_" + fn + ".html"
				with open(fo_snip,'w') as output_file:
					output_file.write(str(markup.prettify()))
			except:
				bad_message = f"Issues generating text - check {url}"
				bad_urls.append(bad_message)
				output_type = "none"
		else:
			bad_message = f"No body tags - check {url}"
			bad_urls.append(bad_message)
	# generate output
	# pdf, word, text, web_page
	# pdf will have full_file_report

	json_data = ""
	rightnow = str(datetime.datetime.now())
	url_report = f'"url":"{url}",'
	initial_save = f'"first_saved":"{rightnow}",'
	accessed_report = f'"accessed_on":"{rightnow}",'
	run_pdf = f'"run_pdf":"y",'
	current_report = f'"current":"yes",'
	if output_type == "text":
		pass

	elif output_type == "word":
		pass

	elif output_type == "pdf":
		## TODO - clean up metadata output and include it in json output
		file_full_report = f'"filename_full":"{file_output}",'
		ft_report = f'"filename_text":"{text_output}",'
		tc_report = f'"text_count":"",'
		#metadata_report = f'"metadata":{pdf_meta}'
		text_hash = f'"text_hash":"{th}"' # when metadata is included add comma at the end of text_hash
		jso_one = netloc + "_" + th + ".json"
		json_out = url_service + "/" + jso_one
		json_data = f"{url_report}{initial_save}{accessed_report}{run_pdf}{current_report}{file_full_report}{ft_report}{text_hash}"
		#json_data = f"{url_report}{initial_save}{accessed_report}{run_pdf}{current_report}{file_full_report}{ft_report}{text_hash}{metadata_report}"
		json_data = "{" + json_data + "}"
		if th in all_hash: # we have a copy of this content
			if jso_one in all_files: # we have a copy of this content from this domain
				with open(json_out) as input:
					data = json.load(input)
					if data['url'] == url: # this file has this content from this url
						# update "accessed_on" value, retain all other values
						data_length = len(data)
						data_count = 0
						new_data = "{ "
						for d,i in data.items():
							data_count += 1
							if d == "accessed_on":
								ar = f'"accessed_on":"{rightnow}"'
								new_data = new_data + ar
							else:
								new_data = new_data + f'"{d}":"{i}"'

							if data_count < data_length:
								new_data = new_data + ","
							elif data_count == data_length:
								new_data = new_data + "}"
						write_file(json_out, new_data) # update existing file with new accessed time
						clean_json(json_out)
					else:
						bad_text = f"Review {jso_one} and {url}. The source url might need to be updated"
						bad_urls.append(bad_text)
			else:
				if url in all_urls:
					bad_text = f"The text at this URL appears to be reused. Investigate {url}"
		elif url in all_urls: # we have the url, but the content is new
			url_updated.append(url)
			# get index of all instances of the url in the list
			# use the index to get corresponding filenames in same index from filename list
			select_index = [i for i, value in enumerate(all_urls) if value == url]
			for si in select_index:
				# for each filename, open file, check url, verify that it's identical
				# check "current" status - if equal "yes" change to "no"				
				file_path = url_service + "/" + all_files[si]
				with open(file_path) as input:
					data = json.load(input)
					if data['current'] == "yes":
						data_length = len(data)
						data_count = 0
						new_data = "{ "
						for d,i in data.items():
							data_count += 1
							if d == "current":
								new_data = new_data + f'"{d}":"no"'
							else:
								new_data = new_data + f'"{d}":"{i}"'

							if data_count < data_length:
								new_data = new_data + ","
							elif data_count == data_length:
								new_data = new_data + "}"
						
						write_file(file_path,new_data) # rewrite file with updated "current" value
						clean_json(file_path)
					else:
						pass
			write_file(json_out, json_data) # write new "current" file
			clean_json(json_out)
		else:
			write_file(json_out, json_data) # create a new record for this url and hash
			clean_json(json_out)
	elif output_type == "web_page":
		ft_report = f'"filename_text":"{fo_text}",'
		tc_report = f'"text_count":"{txt_count}",'
		#snippet
		fn_snip_report = f'"filename_snippet":"{fo_snip}",'
		# full text
		file_full_report = f'"filename_full":"{fo_full}",'
		fc_report = f'"full_count":"{full_page_markup}",'
		first_report = f'"first":"{opening_text}",'
		last_report = f'"last":"{closing_text}",'
		middle_report = f'"middle":"{middle_text}"'
		jso_one = netloc + "_" + th + ".json"
		json_out = url_service + "/" + jso_one
		json_data = f"{url_report}{initial_save}{accessed_report}{current_report}{file_full_report}{fc_report}{ft_report}{tc_report}{text_hash}{fn_snip_report}{first_report}{last_report}{middle_report}"
		json_data = "{" + json_data + "}"
		if th in all_hash: # we have a copy of this content
			if jso_one in all_files: # we have a copy of this content from this domain
				with open(json_out) as input:
					data = json.load(input)
					if data['url'] == url: # this file has this content from this url
						# update "accessed_on" value, retain all other values
						data_length = len(data)
						data_count = 0
						new_data = "{ "
						for d,i in data.items():
							data_count += 1
							if d == "accessed_on":
								ar = f'"accessed_on":"{rightnow}"'
								new_data = new_data + ar
							else:
								new_data = new_data + f'"{d}":"{i}"'

							if data_count < data_length:
								new_data = new_data + ","
							elif data_count == data_length:
								new_data = new_data + "}"
						write_file(json_out, new_data) # update existing file with new accessed time
						clean_json(json_out)
					else:
						bad_text = f"Review {jso_one} and {url}. The source url might need to be updated"
						bad_urls.append(bad_text)
			else:
				if url in all_urls:
					bad_text = f"The text at this URL appears to be reused. Investigate {url}"
		elif url in all_urls: # we have the url, but the content is new
			url_updated.append(url)
			# get index of all instances of the url in the list
			# use the index to get corresponding filenames in same index from filename list
			select_index = [i for i, value in enumerate(all_urls) if value == url]
			for si in select_index:
				# for each filename, open file, check url, verify that it's identical
				# check "current" status - if equal "yes" change to "no"				
				file_path = url_service + "/" + all_files[si]
				with open(file_path) as input:
					data = json.load(input)
					if data['current'] == "yes":
						data_length = len(data)
						data_count = 0
						new_data = "{ "
						for d,i in data.items():
							data_count += 1
							if d == "current":
								new_data = new_data + f'"{d}":"no"'
							else:
								new_data = new_data + f'"{d}":"{i}"'

							if data_count < data_length:
								new_data = new_data + ","
							elif data_count == data_length:
								new_data = new_data + "}"
						
						write_file(file_path,new_data) # rewrite file with updated "current" value
						clean_json(file_path)
					else:
						pass
			write_file(json_out, json_data) # write new "current" file
			clean_json(json_out)
		else:
			write_file(json_out, json_data) # create a new record for this url and hash
			clean_json(json_out)
	else:
		pass

driver.quit()

print("\n* * *\n")
print("URLs processed:")
for p in processed_url:
	print(f' * {p}')

print("\n* * *\n")
print("Some problems to look at:")
for b in bad_urls:
	print(f' * {b}')

if len(url_updated) > 0:
	print("\n* * *\n")
	print("URLs with updates:")
	for u in url_updated:
		print(f' * {u}')
