#import sys, re, string, math
#import nltk
#import pickle 
#from nltk.tokenize import RegexpTokenizer
#from nltk.corpus import stopwords

from gensim.models import Word2Vec
import string

# feed in: a list of sentences, and each sentence is a list of words

modelPath = '../pickledData/w2vModel'

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


#model.similarity('woman', 'man')



#sentences = ["hello, is it me you're looking for".split(), "this is the song that never ends".split()]



# using the brown corpus
#from nltk.corpus import brown
#preprocessWord2VecModel(brown.sents())

#import useW2V
#thisModel = useW2V.word2vecFactory()
#thisModel.getWordVectorFromSentence("This is a sentence, right?", "right", "write")