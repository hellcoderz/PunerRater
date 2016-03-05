import sys, re, string, math, itertools
#import nltk
import pickle 
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from gensim.models import Word2Vec

#unigramF = open("../Lexicons/google_1grams.txt", "r")
modelPath = '../PickledData/w2vModel'
model = Word2Vec.load(modelPath)
unigramDict = pickle.load(open("../PickledData/coca.p", "r"))
homophonesDict = pickle.load(open("../PickledData/homophones.p", "r"))
cmuDict = pickle.load(open("../PickledData/cmu.p", "r"))
#ratingsDict = pickle.load(open("../PickedData/ratings.p", "r"))

#for l in unigramF:
#	l = l.strip().lower()
#	toks = l.split("\t")
#	word = toks[0]
#	freq = toks[1]
#	unigramDict[word] = math.log(float(freq))
print "Finished loading...."

def findHomophone(word):
	if word in cmuDict:
		phones = cmuDict[word]
	else:
		return None
	homophones = homophonesDict[phones]
	#print homophones
	homophones.remove(word)
	#print homophones
	if len(homophones) == 0:
		return None
	elif len(homophones) == 1:
		return homophones[0]
	else:
		return findMostFrequent(homophones)


def findMostFrequent(words):
	freq = float("-inf")
	mostFreqWord = ""
	for w in words:
		thisFreq = getUnigram(w)
		print "w: " + w + " freq: " + str(thisFreq)
		if thisFreq > freq:
			freq = thisFreq
			mostFreqWord = w
	return mostFreqWord

def processSentence(sentence, homophone, alternative, metric="wordnet"):
	print "Sentence: " + sentence
	tokenizer = RegexpTokenizer(r'\w+')
	words = tokenizer.tokenize(sentence.lower())
	contentWords = [word for word in words if word not in stopwords.words('english')]
	print "Content words: " + " ".join(contentWords)
	wordInfoDict = makeWordInfoDict(contentWords, homophone, alternative, metric)
	#wordPairsOrig = getDistances(contentWords, homophone)
	#wordPairsAlt = getDistances(contentWords, alternative)
	
	homophoneProb = getUnigram(homophone)
	alternativeProb = getUnigram(alternative)
	print "Computing measures..."
	measures = computeMeasures(wordInfoDict, homophoneProb, alternativeProb)	
	return measures
	#distinct = measures["KL1"]
	#ambiguity = measures["entropy"]
	#focus1 = measures["m1Focus"]
	#focus2 = measures["m2Focus"]


def computeMeasures(wordInfoDict, m1Prob, m2Prob):
	words = wordInfoDict.keys()
	numWords = len(words)
	focusVectors =list(itertools.product([False, True], repeat=numWords))
        # vector containing probabilities for each f,w combination given m2
    	fWGivenM1 = []
    	fWGivenM2 = []
    	sumOverMF = 0
    	sumM1OverF = 0
    	sumM2OverF = 0
    	# iterates through all subsets of indices in contextSubsets
    	for fVector in focusVectors:
               	# Prior probabilty of a word being in focus (coin weight)
        	probWordInFocus = 0.5 # can be tweaked

        	# Probability of a focus vector
        	# Determined by the number of words in focus (number of "True" in vector) vs not
        	numWordsInFocus = sum(fVector)
        
        	probFVector = math.pow(probWordInFocus, numWordsInFocus) * math.pow(1 - probWordInFocus, numWords - numWordsInFocus)

        	wordsInFocus = []
        	sumLogProbWordsGivenM1F = 0
        	sumLogProbWordsGivenM2F = 0
        	for j in range(numWords):
            		wordj = words[j]
            		if fVector[j] is True:
                		wordsInFocus.append(wordj)
                		#print math.log(0)
				logProbWordGivenM1 = wordInfoDict[wordj][0] + math.log(wordInfoDict[wordj][1]) + 1 
                		logProbWordGivenM2 = wordInfoDict[wordj][0] + math.log(wordInfoDict[wordj][2]) + 1
				sumLogProbWordsGivenM1F = sumLogProbWordsGivenM1F + logProbWordGivenM1
                		sumLogProbWordsGivenM2F = sumLogProbWordsGivenM2F + logProbWordGivenM2
            		else:
                		logProbWordGivenM1_ngram = wordInfoDict[wordj][0]
                		logProbWordGivenM2_ngram = wordInfoDict[wordj][0]
                		sumLogProbWordsGivenM1F = sumLogProbWordsGivenM1F + logProbWordGivenM1_ngram
                		sumLogProbWordsGivenM2F = sumLogProbWordsGivenM2F + logProbWordGivenM2_ngram
        
        	# with homophone prior, calculate P(m,F | words)
        	probM1FGivenWords = math.exp(m1Prob + math.log(probFVector) + sumLogProbWordsGivenM1F)
        	probM2FGivenWords = math.exp(m2Prob + math.log(probFVector) + sumLogProbWordsGivenM2F)
        
        	# P(F | words, m) \propto P(w | m, f)P(f | m)
        	# since f, m are independent, this is just P(f)
        	probFGivenWordsM1 = math.exp(math.log(probFVector) + sumLogProbWordsGivenM1F)
        	probFGivenWordsM2 = math.exp(math.log(probFVector) + sumLogProbWordsGivenM2F)
        	fWGivenM1.append(probFGivenWordsM1)
        	fWGivenM2.append(probFGivenWordsM2)
	# sums over all possible focus vectors for P(m1|w)
    	sumM1OverF = sumM1OverF + probM1FGivenWords
    	sumM2OverF = sumM2OverF + probM2FGivenWords
    	sumOverMF = sumOverMF + probM1FGivenWords + probM2FGivenWords
    	# normalizes and calcualtes entropy
    	probM1 = sumM1OverF / sumOverMF
    	probM2 = sumM2OverF / sumOverMF
    	entropy = - (probM1 * math.log(probM1) + probM2 * math.log(probM2))

    	# normalizes probability vectors of F to sum to 1 for m1 and m2
    	normalizedFWGivenM1 = normListSumTo(fWGivenM1, 1)
    	normalizedFWGivenM2 = normListSumTo(fWGivenM2, 1)

    	maxM1FocusVector = focusVectors[normalizedFWGivenM1.index(max(normalizedFWGivenM1))]
    	maxM2FocusVector = focusVectors[normalizedFWGivenM2.index(max(normalizedFWGivenM2))]

    	# find words in focus given maxM1FocusVector and maxM2FocusVector
    	maxM1FocusWords = []
    	maxM2FocusWords = []
    	for i in range(len(maxM1FocusVector)):
        	if maxM1FocusVector[i] is True:
            		maxM1FocusWords.append(words[i])
        	if maxM2FocusVector[i] is True:
            		maxM2FocusWords.append(words[i])
    	# coomputes KL between the two distributions
    	KL1 = 0
    	KL2 = 0
    	for i in range(len(normalizedFWGivenM1)):
        	KL1 = KL1 + math.log(normalizedFWGivenM1[i] / normalizedFWGivenM2[i]) * normalizedFWGivenM1[i]
        	KL2 = KL2 + math.log(normalizedFWGivenM2[i] / normalizedFWGivenM1[i]) * normalizedFWGivenM2[i]
	measures = dict()
	measures["KL1"] = KL1
	measures["KL2"] = KL2
	measures["entropy"] = entropy
	measures["m1Focus"] = maxM1FocusWords
	measures["m2Focus"] = maxM2FocusWords
   	return measures


def preprocessWord2VecModel(corpus):
    # min_count: minimum word count to keep. Throws out infrequent words
    # size: size of NN layer
    model = Word2Vec(corpus, min_count=10, size=100)
    model.init_sims(replace=True) # finalize the model; no more updating
    model.save(modelPath)



class word2vecFactory(object):
    def __init__(self):
        self.model = Word2Vec.load(modelPath)

    def getWordVectorFromSentence(self, sentence, homophone, alternative):
        '''
        calcualtes the word vector representations of the inputs using the gensim Word2Vec model

        @input:
            sentence: a list of strings
            homophone: single string
            alternative: single string

        @return:
            (sentenceVectors, homophoneVector, alternativeVector)
            sentenceVectors: a list of vectors
            homophoneVector: a single vector
            alternativeVector: a single vector
        '''
        sentenceVectors = [self.model[word.translate(None, string.punctuation)] for word in sentence.split()] 
        homophoneVector = self.model[homophone]
        alternativeVector = self.model[alternative]
        return(sentenceVectors, homophoneVector, alternativeVector)

def makeWordInfoDict(words, h1, h2, metric):
	wordInfoDict = dict()
	for w in words:
		uniProb = getUnigram(w)
		related1 = getMetric(w, h1, metric)
		related2 = getMetric(w, h2, metric)
		wordInfoDict[w] = [uniProb, related1, related2]
	return wordInfoDict

def getMetric(word, h, metric):
	if metric is "wordnet":
		return getWordNetMetric(word, h)
	elif metric is "word2vec":
        	return getWord2VecMetric(word, h)	
	else:
		return 1

def getWordNetMetric(word, h):
	syn1 = wordnet.synsets(word)[0]
	syn2 = wordnet.synsets(h)[0]
	relatedness = syn1.wup_similarity(syn2)
	if relatedness is None:
		relatedness = math.pow(0.1, 10)
	print "Relatedness(" + word + "," + h + "): " + str(relatedness)
	return relatedness
	
#def getPeopleMetric(word, h):
	

def getWord2VecMetric(word, h):
    #print "Loading Word2Vec model"
    return model.similarity(word, h)

def getUnigram(word):
	if word in unigramDict:
		return unigramDict[word]
	else:
		return min(unigramDict.values())

def normListSumTo(L, sumTo=1):
	sum = reduce(lambda x,y:x+y, L)
	return [ x/(sum*1.0)*sumTo for x in L]

#print findHomophone("hare")
#print getWord2VecMetric("apple", "cat")
print processSentence("The dog chased the cat and the cow followed the pig", "animal", "food")
print processSentence("The dog ate the apple and the cat drank the milk", "animal", "food")
print processSentence("The dentist needs to tell the patient the whole tooth", "tooth", "truth")
#print processSentence("The dog ate the apple and the cat drank the milk", "animal", "food", "word2vec")
#print processSentence("The cat sat on the mat and the hare sat on the table", "dog", "chair")
#print processSentence("The magician was so mad he pulled his hare out", "hare", "hair")
#print unigramDict

