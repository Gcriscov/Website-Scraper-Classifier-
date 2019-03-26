# import libraries
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

fname = 'TrainingOEMs.txt'
urllib3.disable_warnings()

def get_dom(url):
	try:
		connection = requests.get(url, verify=False, allow_redirects=True)
		return connection
	except Exception as e: 
		print('Exception:' + e)
	return connection

def get_links(url):
	u = url
	url = get_dom(url)
	tags = BeautifulSoup(url.content, 'lxml').findAll('a', {"href": True})
	href_set = {tag.get('href') for tag in tags}
	return resolve_links((href for href in href_set), u)

def guess_root(links):
    for link in links:
        if link.find('http'):
            parsed_link = urlparse.urlparse(link)
            scheme = parsed_link.scheme + '://'
            netloc = parsed_link.netloc
            return scheme + netloc

def resolve_links(links, url):
	root = str(url)	
	for link in links:
		#link = l.get('href')
		link = urljoin(root, link)
			#try:
			#	m = re.search('href.*?"/(.*?)"', str(link))
			#except:
			#	m = ''
			#	link = ''
			#if m:
			#	link = str(root) + str(m.group(1))
		print(link)
		yield link

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True
 

	
def striphtml(data):
	data = re.sub('<[^<]+?>', ' ', data)
	data = data.replace('\n', ' ')
	data = data.replace('\t', ' ')
	data = data.replace('\r', ' ')
	data = data.replace('\\"', ' ')
	
	data = data.replace('"', '')
	data = data.translate(str.maketrans('', '', string.punctuation))
	data = re.sub(' +', ' ', data)
	data = re.sub('\d+', '0', data)
	data = data.lower()
	
	p = re.compile(r'<.*?>')
	return str(p.sub('', data))
	
with open(fname) as f:
	content = f.readlines();
	for line in content:
		open_page = ''.join(line);
		for link in get_links(open_page):
				with open('out.txt', 'a') as fileID:
					try:
						print('1')
						page = BeautifulSoup(get_dom(link).content, 'lxml')
						body = page
						for script in body('script'):
							script.decompose()
						for script in body('style'):
							script.decompose()	
						for script in body('head'):
							script.decompose()
						text = striphtml(str(body.text))
						print('aici')
						print(text)
						fileID.write(str(text.encode('ascii', 'ignore')))
						#for string in body.stripped_strings:
						#	print(repr(string)))
						#	fileID.write(repr(string).encode('utf-8'))
						#result = filter(visible, page)
						#print(striphtml(str(page.get_text().encode('utf-8'))))
						#print(striphtml(str(page.text)))
						#fileID.write(striphtml(str(page.get_text().encode('utf-8'))))
						#fileID.write(str(page.text.encode('utf-8')))
						print('2')
						# #print(list(result))
						# #for res in list(result):
						# #	print('2.1')
						# #    print(res)
						# #	element = striphtml(str(res))
							# #element = res.get_text()
							# print('3')
							# print(element)
							# print('4')
							# fileID.write(str(element.encode('utf-8')))
					except Exception as e: 
						print(e)
			
		print('***************************************************************************')
