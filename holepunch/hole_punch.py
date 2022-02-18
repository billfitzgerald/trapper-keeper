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
import time
import platform

url_source = "news_domains.csv" # csv file with a single column: url
output_csv = "data_output.csv"

word_list = [
				'privacy', 
				'legal', 
				'terms', 
				'security', 
				'license', 
				'cookie', 
				'プライバシー', 
				'Конфиденциальность', 
				'Integritet', 
				'personvern'
			]

d = datetime.datetime.today()
year = d.strftime("%Y")
month = d.strftime("%m")
day = d.strftime("%d")
hour = d.strftime("%H")
minute = d.strftime("%M")
date_filename = year + "_" + month + "_" + day + "_" + hour + "_" + minute + "_"

output_csv = date_filename + output_csv

profile = webdriver.FirefoxProfile()
profile.set_preference("browser.cache.disk.enable", False)
profile.set_preference("browser.cache.memory.enable", False)
profile.set_preference("browser.cache.offline.enable", False)
profile.set_preference("network.http.use-cache", False) 
driver = webdriver.Firefox(profile)

driver.set_page_load_timeout(60)
fake_it = "<html><head><title>Something is awry</title></head><body><p>Text</p></body></html>"
df_links = pd.DataFrame(columns=['domain', 'url', 'current_url', 'word', 'a_text', 'href', 'current_url'])
df_urls = pd.read_csv(url_source)

# create output file and add header
with open(output_csv, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    header = ['domain', 'url', 'current_url', 'url_match', 'page_title', 'word', 'a_text', 'href']
    writer.writerow(header)

# function for adding data to csv file
def write_csv(row_data, filename):
    with open(filename, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(row_data)

all_count = 0
for c, d in df_urls.iterrows():
	policy_list = []
	fail = "False"
	all_count += 1
	print("* * *\n")
	print(f'Processing record number {all_count}')
	page_title = ""
	row_write = 0
	url = d['url']
	print(f'\nInitial url: {url}\n')
	temp_netloc = tldextract.extract(url) 
	domain = temp_netloc.domain + '.' + temp_netloc.suffix
	driver.delete_all_cookies()
	try:
		#print("\nTry 1\n")
		driver.get(url)
		#print("\nTry 2\n")
		current_url = driver.current_url
		#print("\nTry 3\n")
	except:
		try:
			url = f"https://www.{domain}"
			#print("\nTry 4\n")
			driver.get(url)
			#print("\nTry 5\n")
			current_url = driver.current_url
			#print("\nTry 6\n")
		except:
			fail = "True"
			current_url = "not applicable"
	if current_url[-1] == "/":
		current_url = current_url[:-1]
	else:
		pass
	print(f"Current url: {current_url}")
	if url == current_url:
		url_match = "yes"
	elif str(domain) in str(current_url):
		url_match = "partial"
	else:
		url_match = "no"
	#Selenium hands the page source to Beautiful Soup
	if fail == "True":
		soup = BeautifulSoup(fake_it, 'lxml')
	else:
		soup=BeautifulSoup(driver.page_source, 'lxml')
	body = soup.body
	try:
		page_title = soup.title.get_text(strip=True)
		print(page_title)
	except:
		page_title = "borkfest"
	try:
		links = body.find_all('a', href=True)
		for l in links:
			try:
				href = l['href']
			except:
				href="no link"
			
			try:
				a_text = l.get_text(strip=True)
			except:
				a_text = "no text"
			if href[:4] != "http":
				href = current_url + href
			else:
				pass
			for word in word_list:
				if word in str(href) or word in a_text:
					if href not in policy_list:
						policy_list.append(href)
						print(f" * We have a match for {word}: {href}")
						row_write += 1
						row = [domain, url, current_url, url_match, page_title, word, a_text, href]
						write_csv(row, output_csv)
					else:
						pass
				else:
					pass
				
	except:
		pass

	if row_write == 0:
		if len(current_url) < 1:
			current_url = ""
		else:
			pass
		if len(page_title) < 1:
			page_title = "none"
		else:
			pass
		word = ""
		a_text = ""
		href = ""
		row = [domain, url, current_url, url_match, page_title, word, a_text, href]
		write_csv(row, output_csv)
	else:
		pass

	print("\n * * * \n")
