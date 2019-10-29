from urllib.request import urlopen, Request
import requests
from bs4 import BeautifulSoup
import lxml.html
import urllib.parse as urlparse
from urllib.parse import urljoin
import re
import string
import urllib3
import pandas as pd
import time
import os
import glob
import csv
import xlsxwriter
from itertools import chain
import re
#from signal import *
#import os, time

#def clean(*args):
#    print('Forced exit!')
#    os._exit(0)

#for sig in (SIGABRT, SIGINT, SIGTERM):
#    signal(sig, clean)
list1 = []
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
def get_links_2layers(url):
	list = get_links(url)
	if list != False:
		for link in list:
			list = chain(list, get_links(link))
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
#read elements from different lines from fname in list
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

print('checking XLS file exists')
if os.path.exists('OEM_results_file.xlsx'): # check if file out_company-name.csv exists
	os.remove('OEM_results_file.xlsx')
workbook = xlsxwriter.Workbook('OEM_results_file.xlsx')

print('open page')

index = 0
for line in url_content:
	
	index += 1
	row = 2
	if index == 1:
		open_page = ''.join(line); # take every link from file with company links
	
		if ('\n' in open_page):
			open_page = open_page.replace('\n', '')
			#print('page opened')
		#print("open page:" + open_page)
		try:
			company = re.split('[.]', open_page)[1] # take company name from link
		except Exception as e:
			print(e)
		Email = ('@' + company + '.com')
		tag_content.insert(0, Email)
		#print("company:" + company)
		worksheet = workbook.add_worksheet(company)
		header = [company] + tag_content
		print(header)
		worksheet.write_row('A1', tuple(header)) # write header to file
		
	
	if(nr_layers == 1): # check number of layers to search into
		print('getting links (1)')
		all_links = get_links(open_page)
	elif(nr_layers == 2):
		print('getting links (1)')
		all_links = get_links_2layers(open_page)
		#print(all_links)
	else:
		all_links = ''
		print('*****************     '.join('Empty ').join(urls_file).join(' file.'))
	try:
		print('An error has occur but the exel was saved')
	except Exception as e:
		workbook.close()
		
	if(all_links != False): # check if we there are links in all_links
		print(type(all_links))

		for (link) in all_links: 
			if ('\n' in link):
				print('---------------' + link)
				link = link.replace('\n', '')
			
			com = re.search(open_page, link)
			if not com:
				continue
				
			if link in list1:
				#print("The site was repeting and was skiped")
				#print("test" + link )
				continue	
					
			list1.append(link)

			if(link != False and link.count('.pdf') == 0 and (company in link)):
				# print("aici se verifica" + link)
				
				str_to_file = [link] # create row to insert in file
				
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
						nr_apparitions = str(page).lower().count(tag)
						sum = sum + nr_apparitions
						if(nr_apparitions != 0):
							print(str(nr_apparitions) + '----' + str(tag))
						str_to_file.append(nr_apparitions)
						
							
					if(sum > 0): # if sum == 0, don't write tags to file
						worksheet.write_row('A' + str(row), tuple(str_to_file)) # write values to file
						row = row + 1
						print('Wrote to file')
						
					else:
						print('No tag found')
					
				except Exception as e: 
					print(e)
				#print(page)
			#print('\n')
			time.sleep(0.05) 
	print('***************************************************************************')

workbook.close()