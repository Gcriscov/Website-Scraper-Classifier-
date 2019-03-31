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
import pandas as pd
import time
from flashtext.keyword import KeywordProcessor

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


def sigmoid(x):
    output = 1/(1+np.exp(-x))
    return output

# convert output of sigmoid function to its derivative
def sigmoid_output_to_derivative(output):
    return output*(1-output)
	
	
def clean_up_sentence(sentence):
    # tokenize the pattern
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words
	
def clean_up_sentence(sentence):
    # tokenize the pattern
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words
	
def think(sentence, show_details=False):
    x = bow(sentence.lower(), words, show_details)
    if show_details:
        print ("sentence:", sentence, "\n bow:", x)
    # input layer is our bag of words
    l0 = x
    # matrix multiplication of input and hidden layer
    l1 = sigmoid(np.dot(l0, synapse_0))
    # output layer
    l2 = sigmoid(np.dot(l1, synapse_1))
    return l2


def train(X, y, hidden_neurons=10, alpha=1, epochs=50000, dropout=False, dropout_percent=0.5):

    print ("Training with %s neurons, alpha:%s, dropout:%s %s" % (hidden_neurons, str(alpha), dropout, dropout_percent if dropout else '') )
    print ("Input matrix: %sx%s    Output matrix: %sx%s" % (len(X),len(X[0]),1, len(classes)) )
    np.random.seed(1)

    last_mean_error = 1
    # randomly initialize our weights with mean 0
    synapse_0 = 2*np.random.random((len(X[0]), hidden_neurons)) - 1
    synapse_1 = 2*np.random.random((hidden_neurons, len(classes))) - 1

    prev_synapse_0_weight_update = np.zeros_like(synapse_0)
    prev_synapse_1_weight_update = np.zeros_like(synapse_1)

    synapse_0_direction_count = np.zeros_like(synapse_0)
    synapse_1_direction_count = np.zeros_like(synapse_1)
        
    for j in iter(range(epochs+1)):

        # Feed forward through layers 0, 1, and 2
        layer_0 = X
        layer_1 = sigmoid(np.dot(layer_0, synapse_0))
                
        if(dropout):
            layer_1 *= np.random.binomial([np.ones((len(X),hidden_neurons))],1-dropout_percent)[0] * (1.0/(1-dropout_percent))

        layer_2 = sigmoid(np.dot(layer_1, synapse_1))

        # how much did we miss the target value?
        layer_2_error = y - layer_2

        if (j% 10000) == 0 and j > 5000:
            # if this 10k iteration's error is greater than the last iteration, break out
            if np.mean(np.abs(layer_2_error)) < last_mean_error:
                print ("delta after "+str(j)+" iterations:" + str(np.mean(np.abs(layer_2_error))) )
                last_mean_error = np.mean(np.abs(layer_2_error))
            else:
                print ("break:", np.mean(np.abs(layer_2_error)), ">", last_mean_error )
                break
                
        # in what direction is the target value?
        # were we really sure? if so, don't change too much.
        layer_2_delta = layer_2_error * sigmoid_output_to_derivative(layer_2)

        # how much did each l1 value contribute to the l2 error (according to the weights)?
        layer_1_error = layer_2_delta.dot(synapse_1.T)

        # in what direction is the target l1?
        # were we really sure? if so, don't change too much.
        layer_1_delta = layer_1_error * sigmoid_output_to_derivative(layer_1)
        
        synapse_1_weight_update = (layer_1.T.dot(layer_2_delta))
        synapse_0_weight_update = (layer_0.T.dot(layer_1_delta))
        
        if(j > 0):
            synapse_0_direction_count += np.abs(((synapse_0_weight_update > 0)+0) - ((prev_synapse_0_weight_update > 0) + 0))
            synapse_1_direction_count += np.abs(((synapse_1_weight_update > 0)+0) - ((prev_synapse_1_weight_update > 0) + 0))        
        
        synapse_1 += alpha * synapse_1_weight_update
        synapse_0 += alpha * synapse_0_weight_update
        
        prev_synapse_0_weight_update = synapse_0_weight_update
        prev_synapse_1_weight_update = synapse_1_weight_update

    now = datetime.datetime.now()

    # persist synapses
    synapse = {'synapse0': synapse_0.tolist(), 'synapse1': synapse_1.tolist(),
               'datetime': now.strftime("%Y-%m-%d %H:%M"),
               'words': words,
               'classes': classes
              }
    synapse_file = "synapses.json"


	
with open(fname) as f:
    content = f.readlines();
    for line in content:
        open_page = ''.join(line);
        for link in get_links(open_page):
            with open(str(link) + '.txt', 'a') as fileID:
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
		
		
		
data = pd.read_csv('Classified_data.csv')		
data = data[pd.notnull(data['tokenized_sourcee'])]
data = data[data.Category != 'None']

for index,row in data.iterrows():
    train_data.append({"class":row["Category"], "sentence":row["text"]})


words = []
classes = []
documents = []
ignore_words = ['?']
# loop through each sentence in our training data
for pattern in training_data:
    # tokenize each word in the sentence
    w = nltk.word_tokenize(pattern['sentence'])
    # add to our words list
    words.extend(w)
    # add to documents in our corpus
    documents.append((w, pattern['class']))
    # add to our classes list
    if pattern['class'] not in classes:
        classes.append(pattern['class'])

# stem and lower each word and remove duplicates
words = [stemmer.stem(w.lower()) for w in words if w not in ignore_words]
words = list(set(words))

# remove duplicates
classes = list(set(classes))

print (len(documents), "documents")
print (len(classes), "classes", classes)
print (len(words), "unique stemmed words", words)


from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
# create our training data
training = []
output = []
# create an empty array for our output
output_empty = [0] * len(classes)

# training set, bag of words for each sentence
for doc in documents:
    # initialize our bag of words
    bag = []
    # list of tokenized words for the pattern
    pattern_words = doc[0]
    # stem each word
    pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
    # create our bag of words array
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    training.append(bag)
    # output is a '0' for each tag and '1' for current tag
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    output.append(output_row)

print ("# words", len(words))
print ("# classes", len(classes))


X = np.array(training)
y = np.array(output)

start_time = time.time()

train(X, y, hidden_neurons=10, alpha=0.1, epochs=50000, dropout=False, dropout_percent=0.2)

elapsed_time = time.time() - start_time
print ("processing time:", elapsed_time, "seconds")

    with open(folder_path+synapse_file, 'w') as outfile:
        json.dump(synapse, outfile, indent=4, sort_keys=True)
    print ("saved synapses to:", synapse_file)
	
