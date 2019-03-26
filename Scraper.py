# 3/26/2019
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

# Open url and return page content as BeautifulSoup object
def get_dom(url):
	try:
		connection = requests.get(url, verify=False, allow_redirects=True)
		return connection
	except Exception as e: 
		print(e)
	return connection

# Return links from url
def get_links(url):
	u = url
	url = get_dom(url)
	tags = BeautifulSoup(url.content, 'lxml').findAll('a', {"href": True})
	href_set = {tag.get('href') for tag in tags}
	return resolve_links((href for href in href_set), u)

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
		print("Webpage Link: " + link)
		yield link
# Clean html content
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
                    page = BeautifulSoup(get_dom(link).content, 'lxml')
		
                    for script in page('script'):
                        script.decompose() # delete all script modules
                    for script in page('style'):
                        script.decompose() # delete all style modules
			
                    text = striphtml(str(page.text))
                    print('Content:\n' + str(text.encode('ascii', 'ignore')))
                    fileID.write(str(text.encode('ascii', 'ignore')))
                except Exception as e: 
			print(e)
        print('***************************************************************************')
