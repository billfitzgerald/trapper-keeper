import sys
import re
import os
import datetime
import tldextract
import csv
import json
#import pyfiglet
#import pprint
import requests
import random 
from collections import OrderedDict

def makedirs(directory):
	try:
		os.makedirs(directory)
	except FileExistsError:
		# directory already exists
		pass

def prep_request():
	headers_list = headers_all()
	headers = random.choice(headers_list)
	r = requests.Session()
	r.headers = headers
	return r

# function for adding data to csv file
def write_csv(row_data, outputfile):
    with open(outputfile, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(row_data)

def clean_string(messy_text):
	clean_text = re.sub('[^A-Za-z0-9]+', '_', messy_text)
	clean_text = clean_text.lower()
	return clean_text

def text_excerpt(full_text):
	x = len(full_text)
	if x < 50:
		excerpt = full_text
	elif x >= 50 and x < 150:
		excerpt = full_text[0:20] + " ... " + full_text[x-20:x]
	elif len(full_text) >= 150:
		excerpt = full_text[0:50] + " ... " + full_text[x-50:x]
	else:
		excerpt = "Did not process correctly."

	return excerpt

def compress_text(squish):
	nospace = squish.replace('\r', '').replace('\n', '').replace(' ', '')
	nospace = ''.join(nospace.split())
	return nospace

def pointcalc(calctext, closing, opening, middle, character):
	verify = 0
	textlen = len(calctext)
	open_len = len(opening)
	close_len = len(closing)
	if textlen <= character:
		verify = 0
	elif textlen > character:
		calctext = compress_text(calctext)
		
		if closing in calctext:
			verify += 4
		else:
			pass

		if opening in calctext:
			verify += 2
		else:
			pass

		if middle in calctext:
			verify += 1
		else:
			pass
	else:
		pass

	return verify

def write_file(filename, content):
	with open(filename,'w') as output_file:
		output_file.write(content)

def clean_json(filename):
	f = open(filename,)
	data = json.load(f)
	with open(filename, "w") as wf:
		json.dump(data, wf, indent=2, separators=(", ", ":"))

def headers_all():
	headers_list = [
					# Firefox 77 Mac
					{
					"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
					"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
					"Accept-Language": "en-US,en;q=0.5",
					"Referer": "https://www.google.com/",
					"DNT": "1",
					"Connection": "keep-alive",
					"Upgrade-Insecure-Requests": "1"
					},
					# Firefox 77 Windows
					{
					"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
					"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
					"Accept-Language": "en-US,en;q=0.5",
					"Accept-Encoding": "gzip, deflate, br",
					"Referer": "https://www.google.com/",
					"DNT": "1",
					"Connection": "keep-alive",
					"Upgrade-Insecure-Requests": "1"
					},
					# Chrome 83 Mac
					{
					"Connection": "keep-alive",
					"DNT": "1",
					"Upgrade-Insecure-Requests": "1",
					"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
					"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
					"Sec-Fetch-Site": "none",
					"Sec-Fetch-Mode": "navigate",
					"Sec-Fetch-Dest": "document",
					"Referer": "https://www.google.com/",
					"Accept-Encoding": "gzip, deflate, br",
					"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
					},
					# Chrome 83 Windows 
					{
					"Connection": "keep-alive",
					"Upgrade-Insecure-Requests": "1",
					"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
					"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
					"Sec-Fetch-Site": "same-origin",
					"Sec-Fetch-Mode": "navigate",
					"Sec-Fetch-User": "?1",
					"Sec-Fetch-Dest": "document",
					"Referer": "https://www.google.com/",
					"Accept-Encoding": "gzip, deflate, br",
					"Accept-Language": "en-US,en;q=0.9"
					}
					]

	return headers_list

def rando_url():
	random_site_list = [
		'https://mensgear.net/weird-converter/',
		'http://www.internetisshit.org/',
		'https://www.howmanypeopleareinspacerightnow.com/',
		'http://strangehorizons.com/non-fiction/articles/installing-linux-on-a-dead-badger-users-notes/',
		'http://dogs.are.the.most.moe/',
		'http://www.myhousematesdiary.com/',
		'http://salmonofcapistrano.com/',
		'https://bouncingdvdlogo.com/',
		'http://www.icbe.org/',
		'http://salmonofcapistrano.com/',
		'https://badkidsjokes.tumblr.com/',
		'https://www.tumblr.com/login_required/ihumans',
		'http://hardcoreprawnlawn.com/',
		'https://www.youtube.com/watch?v=9C_HReR_McQ&feature=emb_logo',
		'http://www.woot.co.uk/',
		'https://www.omfgdogs.com/',
		'https://codepen.io/ge1doot/full/WbWQOP/',
		'http://www.madsci.org/cgi-bin/lynn/jardin/SCG',
		'http://www.humanforsale.com/',
		'https://www.onemilliongiraffes.com/',
		'http://zoomquilt.org/',
		'http://www.youareinaforest.com/',
		'http://hyperboleandahalf.blogspot.com/',
		'https://www.worldbeardchampionships.com/photos/',
		'https://corgiorgy.com/',
		'https://www.genderanalyzer.com/',
		'https://www.howmanypeopleareinspacerightnow.com/',
		'http://beesbeesbees.com/',
		'https://scienceblogs.com/goodmath/2006/10/12/who-needs-a-calculator-multipl',
		'http://www.fincher.org/Misc/Pennies/BigTower.shtml',
		'https://www.tumblr.com/login_required/ihumans',
		'http://inventorspot.com/articles/body_bread_13546',
		'http://www.thesmokinggun.com/time-waster',
		'http://www.therestartpage.com/',
		'http://www.museumofconceptualart.com/accomplished/index.html',
		'https://www.youtube.com/askaninja',
		'http://zoomquilt.org/',
		'http://www.fincher.org/Misc/Pennies/BigTower.shtml',
		'http://alpha61.com/primenumbershittingbear/',
		'http://www.muppetlabs.com/~breadbox/txt/al.html',
		'https://www.nobodyhere.com/justme/me.here',
		'http://5secondfilms.com/',
		'https://isitchristmas.com/',
		'http://themostseconds.com/',
		'https://garfieldminusgarfield.net/',
		'http://cachemonet.com/',
		'http://ihasabucket.com/',
		'http://www.ihatecilantro.com/',
		'http://grandpanoclothes.com/',
		'http://www.everydayim.com/',
		'http://www.republiquedesmangues.fr/',
		'http://dogs.are.the.most.moe/',
		'http://zombo.com/',
		'http://eelslap.com/',
		'https://swatblog.rtgp.xyz/',
		'https://mensgear.net/weird-converter/',
		'http://randomcolour.com/',
		'http://eelslap.com/',
		'https://trypap.com/',
		'http://www.koalastothemax.com/',
		'http://www.republiquedesmangues.fr/',
		'http://www.movenowthinklater.com/',
		'http://www.partridgegetslucky.com/',
		'https://hooooooooo.com/',
		'https://www.findagrave.com/',
		'http://www.cachemonet.com/',
		'http://www.coincalc.com/',
		'https://www.sarina-brewer.com/',
		'http://www.lileks.com/oldads/index.html',
		'http://www.staggeringbeauty.com/',
		'https://thatsthefinger.com/',
		'https://cant-not-tweet-this.com/',
	]

	rando = random.choice(random_site_list)
	return rando
