# MUST DOWNLOAD:
# NLTK
## NLTK punkt
## NLTK wordnet
## NLTK vader_lexicon
## NLTK averaged_perceptron_tagger
#
# pattern

import string
from string import punctuation
import re
from random import randint
import socket
import sys
import nltk
import pickle
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import wordnet
from pattern.en import suggest

t = 120 #socket timeout in seconds
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = '127.0.0.1'
dstPort = int(sys.argv[1])
convoFile = open("convo.dat", "r")
topic = 0 #current topic
seq = 0 #current line of topic
memory = {} #holds user answers as dictionary (eg, {"name": "Sam"})
saveAnswer = False #whether to expect an answer to put into 'memory'
posNext = False #whether to expect an answer where positivity level must be determined
lastAnswer = "" #holds last saved answer variable (eg, 'name')
lastType = "" #holds word type of expected answer (eg, 'NNP' [proper noun])
#load tokenizer
with open('sent_tokenizer.pickle', 'rb') as f:
	tokenizer = pickle.load(f)

#try to get word stem
def lemma(word):
	l = nltk.WordNetLemmatizer()

	if l.lemmatize(word, pos='v') != word:
		stem = l.lemmatize(word, pos='v')
	else:
		stem = l.lemmatize(word)

	return stem

#shortens 3+ occurences of same character in a row down to 2
def shortenWords(uIn):
	pattern = re.compile(r"(.)\1{2,}")
	return pattern.sub(r"\1\1", uIn)

#spellcheck a string
def spellCheck(uIn):
	uIn = shortenWords(uIn)
	unchecked = uIn.split(' ')
	checked = ""
	end = ""

	#preserves punctuation at end of user's input
	if any(p in uIn[-1:] for p in punctuation):
		end = uIn[-1:]

	first = True #check for first run to prevent leading space
	for w in unchecked:
		suggestion = suggest(w)
		word = suggestion[0][0]
		for i in suggestion:
			if (w == i[0] or w[0].isupper()):
				word = w
		if not first:
			checked += ' '
		else:
			first = False
		checked += word
	return checked + end

#get the relevant word from the user's answer
def findAnswer(uIn, wordType):
	global tokenizer

	#if only one word is found
	if len(uIn.split(' ')) == 1:
		return lemma(uIn)

	#tokenize user's sentence, breaking into words
	tokenized = tokenizer.tokenize(uIn)
	tagged = list()
	matches = 0
	worseType = wordType[:-1]
	worseMatches = 0

	try:
		for t in tokenized:
			words = nltk.word_tokenize(t)
			tagged += list(nltk.pos_tag(words))

		#find matches for word type specified in convo file (eg, NNP, VB)
		numWords = len(tagged)
		for i in range(0, numWords):
			if tagged[i][0] == "like":
				pass
			elif tagged[i][1] == wordType:
				matches += 1
			elif worseType in tagged[i][1]:
				worseMatches += 1

		# finds best answer found in user's sentence. if none, returns NaN
		answer = "NaN"
		if matches >= 1:
			for i in range(len(tagged)-1, -1, -1):
				if tagged[i][1] == wordType:
					answer = lemma(tagged[i][0])
					if "NN" not in tagged[i][1]:
						answer = answer.lower()
					return answer
		elif worseMatches >= 1:
			for i in range(len(tagged)-1, -1, -1):
				if tagged[i][0] == "like":
					pass
				elif worseType in tagged[i][1]:
					answer = lemma(tagged[i][0])
					if "NN" not in tagged[i][1]:
						answer = answer.lower()
					return answer
		return answer
	except Exception as e:
		print(str(e))

#choose response depending on positivity of user's last answer
def posResponse(uIn):
	global posNext

	#find user response happiness score and find appropriate response
	#note: pos & neg score thresholds may require more testing
	sid = SentimentIntensityAnalyzer()
	scores = sid.polarity_scores(uIn) #scores the users input based on positivity
	line = convoFile.readline()
	if scores['pos'] > 0.7:
		while line[:1] != '+':
			line = convoFile.readline()
	elif scores['neg'] > 0.4:
		while line[:1] != '-':
			line = convoFile.readline()
	else:
		while line[:1] != '0':
			line = convoFile.readline()
	line = line[1:] #remove placeholder character (+, -, 0)
	posNext = False #resets global flag

	return line

#find if any word in a string array (words) is in a string (uIn) or its synonyms
def findWord(words, uIn):
	#remove punctuation from user input and split into words
	user = uIn.translate(str.maketrans('', '', string.punctuation)).split(' ')

	#compare all synonyms of each word in 's' to each word in 'words'
	for uw in user:
		synonyms = [uw]
		for syn in wordnet.synsets(uw):
			for lem in syn.lemmas():
				synonyms.append(lem.name())
		for w in words:
			if w in synonyms:
				return True

#checks if current topic has more lines or not
def topicContinues():
	if getTopic(seq) == '\n':
		return False
	else:
		return True

#get a line by line number
#def getLine(lineNumber):
#	convoFile.seek(0)
#	for i, line in convoFile:
#		if i == lineNumber-1:
#			return line

#get a line by string search
#def findLine(str):
#	convoFile.seek(0)
#	for line in convoFile:
#		if str in line:
#			return line

#get a line by topic number (and sequence number if specified)
def getTopic(sequence=2):
	global topic
	global seq

	count = -1 #keep track of current topic in file
	convoFile.seek(0)
	while True:
		line = convoFile.readline()
		if not line: break
		if line == "\n":
			count += 1
		if count == topic:
			for i in range(0, sequence): #get current line of topic
				line = convoFile.readline()
			return line
	return "Response not found"

#sends the found response, dealing with placeholder values
def sendResponse(response):
	global s
	global saveAnswer
	global lastAnswer
	global lastType
	global seq
	global posNext

	#skips irrelevant positivity responses
	while response[:1] == '+' or response[:1] == '-' or response[:1] == '0':
		response = convoFile.readline()

	if '$' in response: #deals with $ (variable placeholders)
		r = response.split(' ')
		for w in r:
			if '$' in w:
				r2 = w
		index = r.index(r2)
		r2 = r2.translate(str.maketrans('', '', string.punctuation))
		if r2[-1:] == '\n':
			r2 = r2[:-1]
		if r2 in memory: #checks if requested answer is saved in memory. otherwise, displays NaN
			response = response.replace('$' + r2, memory[r2])
		else:
			response = response.replace('$' + r2, "NaN")
	if '+' in response: #deals with + (indicating user response positivity important in next reply)
		response = response.replace('+', '')
		posNext = True
	if '^' in response: #deals with ^ (indicating must find answer in user's next response)
		r = response.split('^')
		r2 = r[1].split('.')
		saveAnswer = True
		lastAnswer = r2[0]
		lastType = r2[1][:-1]
		output = r[0]
	else:
		output = response

	# remove newline character
	if output[-1:] == '\n':
		output = output[:-1]
	# send final output to web server and increment seq
	print("Sent: " + output)
	s.sendto(output.encode('utf-8'), (host, dstPort))
	seq += 1

#finds most appropriate topic from user input
def findTopic(uIn):
	global topic
	global saveAnswer
	global seq
	maxCorr = 0 #keyword match correlation
	topMatch = -1 #best topic match
	matches = 0 #keyword matches for current topic
	count = 0 #keep track of current topic in file
	numKeywords = 0 #holds number of keywords for each topic (used to calculate correlation)
	firstLine = True #keep track of whether next line is the start of a new topic

	#go through convo file, finding best match topic for user's sentence
	convoFile.seek(0)
	convoFile.readline()

	while True: #loop until end of file
		line = convoFile.readline()
		if not line: break
		if firstLine: #on the first line of each topic, gather keywords and compare user's input
			andSplit = line[1:-1].split('&')
			numKeywords = len(andSplit)
			for a in andSplit:
				orSplit = a.split('/')
				if findWord(orSplit, uIn): #if keyword is found in user input, increment matches counter
					matches += 1
			firstLine = False
		elif line == "\n": #at the end of each topic, compute keyword correlation with user's input
			if (matches/numKeywords) > maxCorr: #if highest correlation so far, replace topMatch with current
				maxCorr = matches/numKeywords
				topMatch = count
			matches = 0
			firstLine = True
			count += 1

	#if correlation of best topic above acceptable value, use that topic
	if maxCorr >= 0.5:
		topic = topMatch
		seq = 2
		return getTopic()
	#otherwise if max correlation is poor:
	else: #continue topic if possible. otherwise, give user a default response
		if uIn[-1:] == '?':
			if topicContinues():
				if saveAnswer == True: #if user asked unknown question while expecting answer, repeat question
					seq -= 1
					return getTopic(seq)
				if posNext == True:
					return posResponse(uIn)
				else: #if user asked question and not expecting answer, continue topic
					return getTopic(seq)
			else: #if not in the middle of a topic and user asks question, give a random default question response
				topic = randint(5,9)
				seq = 2
				return getTopic()
		else: #if user says unknown statement, give a random default statement response
			topic = randint(0,4)
			seq = 2
			return getTopic()

#gets next response
def getResponse(uIn=""):
	global seq

	if '?' in uIn: #if user asked a question
		sendResponse(findTopic(uIn))
	elif posNext == True: #if user didn't ask a question, and expect a pos/neg/neutral response next
		sendResponse(posResponse(uIn))
	else:
		line = convoFile.readline()
		if line != "\n": #if current topic has more lines, continue
			sendResponse(line)
		else: #reset sequence and find new topic
			seq = 2
			sendResponse(findTopic(uIn))

#start of program & conversation
uIn = "" #user input variable
s.settimeout(t) #set socket timeout
s.sendto("CONNECT".encode('utf-8'), (host, dstPort))
timeout = False #timeout flag

#exit conversation when user input contains "bye" or "exit", or if socket times out
while "bye" not in uIn.lower() and "exit" not in uIn.lower() and not timeout:
	if uIn != "": #make sure input isn't blank
		if saveAnswer == True and '?' not in uIn: #check if answer is expected to be saved
			tagged = findAnswer(uIn, lastType)
			memory[lastAnswer] = tagged
			saveAnswer = False
		getResponse(uIn.lower())

	try:
		print("Receiving..")
		uIn, server = s.recvfrom(1024) #get user input from web server
		uIn = uIn.decode("utf-8")
		print("Received: " + uIn)
		uIn = spellCheck(uIn)
	except socket.timeout:
		timeout = True

sendResponse("See you soon!")
convoFile.close()
s.close()
exit()