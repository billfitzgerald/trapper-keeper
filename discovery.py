from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import webbrowser
import pandas as pd
import tldextract

source = "url_list" # file, url_list

#set source of urls
url_list = "test_source.csv" # csv file with one column: source_url

#if working from a local file, set info here
file = 'name.html' # html file that has been downloaded and stored locally
file_link = "https://foo.com" # base domain of the url for the file

#Don't change values below this line unless you are willing to break stuff!

base_unique = []
full_url = []
checked_url = []

profile = webdriver.FirefoxProfile()
profile.set_preference("browser.cache.disk.enable", False)
profile.set_preference("browser.cache.memory.enable", False)
profile.set_preference("browser.cache.offline.enable", False)
profile.set_preference("network.http.use-cache", False) 
driver = webdriver.Firefox(profile)

# dataframes
df_all_links = pd.DataFrame(columns=['page', 'link', 'sequence'])

def check_this(fu):
	if fu[0:4] == "http":
		print(f'Do you want to open {fu}?')
		p1 = input("Y to open, N to skip.\n")
		if p1 == "Y":
			if fu not in checked_url:
				checked_url.append(fu)
				webbrowser.open(fu)
				print(f'Do you want to save snapshot of {fu} to the Internet Archive?')
				p2 = input("Y to save, N to skip.\n")
				if p2 == "Y":
					fu_archive = f'https://web.archive.org/save/{fu}'
					webbrowser.open(fu_archive)
				else:
					pass
			else:
				pass
		else:
			pass

def get_all_links(source_doc, url):
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
		get_all_links(data, current_url)
		#soup=BeautifulSoup(driver.page_source, 'lxml')
elif source == "file":
	with open(file) as data:
		get_all_links(data)
else:
	pass

df_all_links.to_csv('all_links.csv', encoding='utf-8', index=False)		