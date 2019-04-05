from urllib.request import urlopen, Request
import requests
from bs4 import BeautifulSoup
import lxml.html
import urllib.parse as urlparse
from urllib.parse import urljoin
import re
import nltk
import string
import urllib3
import pandas as pd
import time
import os
import glob
import csv
import xlwt
urls_file = 'TrainingOEMs.txt'
tags_file = 'tags_file.txt'
urllib3.disable_warnings()

# Open url and return page content as BeautifulSoup object
def get_dom(url):
	try:
		connection = requests.get(url, verify=False, allow_redirects=True)
		return connection
	except Exception as e: 
		print(e)
	return False

# Return links from url
def get_links(url):
	u = url
	url = get_dom(url)
	if url != False:
		tags = BeautifulSoup(url.content, 'lxml').findAll('a', {"href": True})
		href_set = {tag.get('href') for tag in tags}
		return resolve_links((href for href in href_set), u)
	else:
		return False

# Return links url ( 2 layers: all links found un url page + all links on those pages)
def get_links_2layers(url, nr_layers):
	list = get_links(url)
	if list != False:
		for link in list:
			list = list + get_links(link)
		return list
	else:
		return False

# Guess root for relative links
def guess_root(links):
    for link in links:
        if link.find('http'):
            parsed_link = urlparse.urlparse(link)
            scheme = parsed_link.scheme + '://'
            netloc = parsed_link.netloc
            return scheme + netloc

# Transform relative link to absolute link
def resolve_links(links, url):
	root = str(url)	
	for link in links:
		link = urljoin(root, link)
		
		yield link
# read elements from different lines from fname in list
def readFile(fname):
	list = []
	with open(fname) as f:
		content = f.readlines();
		for line in content:	
			list.append(line)
	return list
	
# check if link has company name in it
def checkLink(link, root):
	found = ''
	m = re.search('www(.+?).com', root)
	if m in link:
		return True
	return False
	
def findTagsOnPage(tag, page):
	nr_apparitions = page.count(' ' + tag)
	with open('out.txt', 'a') as fileID:
		fileID.write(tag.join(' ').join(nr_apparitions))
	return

url_content = readFile(urls_file)
tag_content = readFile(tags_file)
nr_layers = int(tag_content[0])
tag_content.pop(0)
tag_content = list({t.lower().strip('\n') for t in tag_content})

for line in url_content:
	open_page = ''.join(line);
	
	company = re.split('[.]', open_page)[1]
	if company is None:
		print('Invalid company name.')
	else:
		print('Company: ' + company)
		company = company
		if os.path.exists('out_' + company + '.csv'):
			os.remove('out_' + company+ '.csv')
		else:
			print("The file does not exist")
		with open('out_' + company+ '.csv', 'a') as fileID:
			s = ''
			for t in tag_content:
				s = s + ',' + t 
			fileID.write(company + s + '\n')
			
		if(nr_layers == 1):
			all_links = get_links(open_page)
		elif(nr_layers == 2):
			all_links = get_links_2layers(open_page)
		else:
			all_links = ''
			print('*****************     '.join('Empty ').join(urls_file).join(' file.'))
		print('***********************' )
		if(all_links != False):
			for link in sorted(all_links):
				if(link != False or link.count('.pdf') == 0):
					str_to_file = link
					print(company)
					try:
						print("Webpage Link: " + link)
						page = BeautifulSoup(get_dom(link).content, 'lxml')
						
						for script in page('script'):
							script.decompose() # delete all script modules
						for script in page('style'):
							script.decompose() # delete all style modules
						for i in range(0, len(tag_content)):
							tag = tag_content[i]
							nr_apparitions = str(page).lower().count(' ' + tag)
							print(str(nr_apparitions) + '---' + tag)
							str_to_file = str_to_file + ',' + str(nr_apparitions)
						
						with open('out_' + company + '.csv', 'a') as fileID:
							fileID.write(str(str_to_file) + '\n')
							
					except Exception as e: 
						print(e)
				else:
					print('Can not open URL: ' + open_page)
		else:
			print('Can not open URL: ' + open_page)
	print('***************************************************************************')
	
for csvfile in glob.glob(os.path.join('.', 'out_*.csv')):
    wb = xlwt.Workbook()
    fpath = csvfile.split("/", 1)
    fname = fpath[1].split(".", 1) ## fname[0] should be our worksheet name

    ws = wb.add_sheet(fname[0])
    with open(csvfile, 'rb') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            for c, col in enumerate(row):
                ws.write(r, c, col)
    wb.save('OEM_tags_out.xls')
	
	
