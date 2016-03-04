import sys, re, string, math
import nltk
import pickle 
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

#unigramF = open("../Lexicons/google_1grams.txt", "r")
unigramDict = pickle.load(open("../PickledData/coca.p", "r"))
#for l in unigramF:
#	l = l.strip().lower()
#	toks = l.split("\t")
#	word = toks[0]
#	freq = toks[1]
#	unigramDict[word] = math.log(float(freq))
#print "loaded"

def processSentence(sentence, homophone, alternative):
	tokenizer = RegexpTokenizer(r'\w+')
	words = tokenizer.tokenize(sentence.lower())
	contentWords = [word for word in words if word not in stopwords.words('english')]
	
	#wordInfoDict = makeWordInfoDict(contentWords, homophone, alternative)
	#wordPairsOrig = getDistances(contentWords, homophone)
	#wordPairsAlt = getDistances(contentWords, alternative)
	
	wordsProbs = [getUnigram(word) for word in words]
	homophoneProb = getUnigram(homophone)
	alternativeProb = getUnigram(alternative)
	#return wordPairsOrig
	#distancesOrig = 
	#distancesAlt = 
	return homophoneProb

def makeWordInfoDict(words, h1, h2):
	wordInfoDict = dict()
	for w in words:
		uniProb = getUnigram(w)
		distance1 = getDistance(w, h1)
		distance2 = getDistance(w, h2)
		wordInfoDict[w] = [uniProb, distance1, distance2]
	return wordInfoDict

#def getDistance(word, h)
def getUnigram(word):
	return unigramDict[word]

print processSentence("This is a sentence, right?", "right", "write")
#print unigramDict

