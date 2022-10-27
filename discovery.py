from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import datetime
import webbrowser
import pandas as pd
import tldextract

source = "url_list" # file, url_list
check_presence = "N" # Y/N value - check for presence of specific urls

#set source of urls
url_list = "discovery_source/test_source.csv" # csv file with one column: source_url
url_check = "discovery_source/check_links.csv" # csv file of urls to check whether or not they are present - one column 'check'

#if working from a local file, set info here
file = 'discovery_source/name.html' # html file that has been downloaded and stored locally
file_link = "https://foo.com" # base domain of the url for the file

#Don't change values below this line unless you are willing to break stuff!

base_unique = []
full_url = []
checked_url = []
skipped_url = []
archived_links = []

profile = webdriver.FirefoxProfile()
profile.set_preference("browser.cache.disk.enable", False)
profile.set_preference("browser.cache.memory.enable", False)
profile.set_preference("browser.cache.offline.enable", False)
profile.set_preference("network.http.use-cache", False) 
driver = webdriver.Firefox(profile)

d = datetime.datetime.today()
year = d.strftime("%Y")
month = d.strftime("%m")
day = d.strftime("%d")
hour = d.strftime("%H")
minute = d.strftime("%M")

file_prefix = f'{month}_{day}_{year}_{hour}_{minute}'
all_links_filename = f'{file_prefix}_all_links.csv'

# dataframes
df_all_links = pd.DataFrame(columns=['page', 'link', 'sequence'])

def save_to_archive(link):
	print(f'Do you want to save a snapshot of {link} to the Internet Archive?')
	p2 = input("Y to save, N to skip.\n")
	if p2 == "Y":
		fu_archive = f'https://web.archive.org/save/{link}'
		webbrowser.open(fu_archive)
		archived_links.append(link)
	else:
		pass

def check_this(fu):
	if fu[0:4] == "http":
		if fu in skipped_url:
			pass
		else:
			print(f'Do you want to open {fu}?')
			p1 = input("Y to open, N to skip.\n")
			if p1 == "Y":
				if fu in checked_url:
					print(f'{fu} has already been reviewed.\n')
					move_one = input("Enter any letter to continue.\n")
					skipped_url.append(fu)
					if len(move_one) > 0:
						pass
					else:
						pass
				elif fu not in checked_url:
					checked_url.append(fu)
					skipped_url.append(fu)
					webbrowser.open(fu)
					save_to_archive(fu)
				else:
					pass
			else:
				skipped_url.append(fu)
	else:
		pass

def get_all_links(source_doc, url):
	full_url = []
	soup=BeautifulSoup(source_doc, 'lxml')
	count = 0
	url_count = 0
	if source == "url_list":
		temp_netloc = tldextract.extract(url)
		file_link = f'https://{temp_netloc.subdomain}.{temp_netloc.domain}.{temp_netloc.suffix}'
	else:
		pass
	for l in soup.find_all('a'):
		count += 1
		try:
			base = l.get('href')
			
			if base[-1] == "/" or base[-1] == "#":
				base = base[:-1]
			else:
				pass
			
			if base[0:3] == "tel":
				url_full = base
			elif base[0:4] != "http":
				url_full = f'{file_link}{base}'
			elif base[0] == "/":
				url_full = f'{file_link}{base}'
			else:
				url_full = base
			df_all_links.loc[df_all_links.shape[0]] = [url, url_full, count]

			if base not in base_unique:
				url_count += 1
				base_unique.append(base)
				if base[0:3] == "tel":
					url_complete = base
				elif base[0:4] != "http":
					url_complete = f'{file_link}{base}'
				elif base[0] == "/":
					url_complete = f'{file_link}{base}'
				else:
					url_complete = base
				if url_complete not in full_url:
					full_url.append(url_complete)
				else:
					pass
			else:
				pass
		except:
			pass	
			
	print ('-'*20)
	print(f'\n{url_count} unique links out of {count} total links\n')
	print ('-'*20)

	view = input("Do you want to select URLs to view in your browser? (Y/N)\n\n")
	if view == "Y":
		for fu in full_url:
			check_this(fu)
	else:
		pass

## End Functions

if source == "url_list":
	thank_you = pd.read_csv(url_list, delimiter=',', quotechar='"',)
	for i, j in thank_you.iterrows():
		url = j.source_url # url to retrieve
		driver.get(url)
		current_url = driver.current_url
		#Selenium hands the page source to Beautiful Soup
		data = driver.page_source
		save_to_archive(current_url)
		get_all_links(data, current_url)
elif source == "file":
	with open(file) as data:
		get_all_links(data)
else:
	pass

driver.quit()

presence_list = []
if check_presence == "Y":
	present_txt = ""
	not_present_txt = ""
	try:
		df_check = pd.read_csv(url_check, delimiter=',', quotechar='"',)
		for a, b in df_check.iterrows():
			ch_url = b.check
			if ch_url[0:7] == "http://":
				ch_url = ch_url.replace("http://", "")
			elif ch_url[0:8] == "https://":
				ch_url = ch_url.replace("https://", "")
			else:
				pass

			if ch_url[0:4] == "www.":
				ch_url = ch_url.replace("www.","")
			else:
				pass
			if ch_url[-1] == "/":
				ch_url = ch_url.rstrip(ch_url[-1])
			presence_list.append(ch_url)

		for p in presence_list:
			link_count = df_all_links['link'].str.contains(p).sum()
			if link_count > 0:
				if link_count == 1:
					present_txt = present_txt + f'\n## {p} appears {link_count} time.\n'
				else:
					present_txt = present_txt + f'\n## {p} appears {link_count} times.\n'
				df_filtered_links = df_all_links[df_all_links['link'].str.contains(p)]
				for m, n in df_filtered_links.iterrows():
					page = n.page
					link = n.link
					present_txt = present_txt + f' * {link} appears on {page}\n'
					#print(f' * {link} appears on {page}')					
			else:
				not_present_txt = not_present_txt + f' * {p} does not appear.\n'
	except:
		print("Do you have a file of urls to check?\n")
		print("Review what's stored at 'url_check'.")
else:
	pass

if check_presence == "Y":
	print(present_txt)
	print(not_present_txt)
else:
	pass

if len(archived_links) > 0:
	print('## These urls were archived:\n')
	for a in archived_links:
		print(f' * {a}')
else:
	print('## No urls were archived.\n')

if len(checked_url) > 0:
	print('## These urls were opened in a browser and reviewed:\n')
	for c in checked_url:
		print(f' * {c}')


df_all_links.to_csv(all_links_filename, encoding='utf-8', index=False)
