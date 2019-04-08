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

url_content = readFile(urls_file) # file with company links
url_content.pop(0)
tag_content = readFile(tags_file) # file with tags
tag_content.pop(0) # delete first row from tag file - comment
tag_content.pop(0) # delete second row from tag file - comment
nr_layers = int(tag_content[0]) # number of layers to search in
tag_content.pop(0) # delete third row from tag list (number of layers)
tag_content.pop(0)
tag_content = list({t.lower().strip('\n') for t in tag_content}) # list with tags
print(tag_content)
for line in url_content:
	open_page = ''.join(line); # take every link from file with company links
	if ('\n' in open_page):
		print('---------------' + open_page)
		open_page = open_page.replace('\n', '')
	company = re.split('[.]', open_page)[1] # take company name from link 
	if company is None: 
		print('Invalid company name.')
	else:
		print('Company: ' + company)
		company = company
		if os.path.exists('out_' + company + '.csv'): # check if file out_company-name.csv exists
			os.remove('out_' + company+ '.csv') # delete any old file
		with open('out_' + company+ '.csv', 'a') as fileID: # create new file
			s = ''
			for t in tag_content: # set column titles as tag names
				s = s + ',' + t 
			fileID.write(company + s + '\n') # write header to file
			
		if(nr_layers == 1): # check number of layers to search into
			all_links = get_links(open_page)
		elif(nr_layers == 2):
			all_links = get_links_2layers(open_page)
		else:
			all_links = ''
			print('*****************     '.join('Empty ').join(urls_file).join(' file.'))
		if(all_links != False): # check if we there are links in all_links
			for link in sorted(all_links): 
				if ('\n' in link):
					print('---------------' + link)
					link = link.replace('\n', '')
				if(link != False and link.count('.pdf') == 0 and (company in link)):
					str_to_file = link # create row to insert in file
					
					try:
						print("Webpage Link: " + link)
						cont = get_dom(link).content
						if (cont == False):
							break
						page = BeautifulSoup(cont, 'lxml')
						for script in page('script'):
							script.decompose() # delete all script modules
						for script in page('style'):
							script.decompose() # delete all style modules
						sum = 0 # sum - counts all apparitions of tags
						for i in range(0, len(tag_content)):
							tag = tag_content[i]
							nr_apparitions = str(page).lower().count(' ' + tag)
							sum = sum + nr_apparitions
							if(nr_apparitions != 0):
								print(str(nr_apparitions) + '----' + str(tag))
							str_to_file = str_to_file + ',' + str(nr_apparitions)
						if(sum > 0): # if sum == 0, don't write tags to file
							with open('out_' + company + '.csv', 'a') as fileID:
								fileID.write(str(str_to_file) + '\n')
							print('Wrote to file')
						else:
							print('No tag found')
					except Exception as e: 
						print(e)
				else:
					print('Can not open URL: ' + open_page)
				print('\n')
				time.sleep(1) 
	print('***************************************************************************')

out_files = [filename for filename in os.listdir('.') if filename.startswith("out_")]
for file in out_files:
	with open(file, 'r') as fileID:
		content = fileID.readFile()
		


