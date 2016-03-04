import sys, re, string

#f = open("sentences.csv", "r")
f = open(sys.argv[1], "r")
functionWords = open("functionWords.txt", "r")

functionDict = dict()

# puts all the function words in a dictionary
for l in functionWords:
    fw = l.replace("\n", "").split("\t")[0]
    fw = fw.replace(" ", "")
    functionDict[fw.lower()] = 0

#for k, v in functionDict.iteritems():
    #print k,
    
firstline = 0
for l in f:
    l = l.replace("\n", "")
    if firstline == 0:
        firstline = 1
    else:
        toks = l.split(",")
        sentenceID = toks[0]
        phoneticID = toks[1]
        version = toks[5]
        h1 = toks[2]
        h2 = toks[3]
        sentence = toks[4].lower().replace('"', "")
        words = sentence.split(" ")
        #print words
        for word in words:
            if "#" not in word:
                word = word.translate(None, '!?.,;:')
                if word not in functionDict.keys() and word is not "":
                    print version + "," + sentenceID + "," + phoneticID + ",a," + h1 + "," + word
                    print version + "," + sentenceID + "," + phoneticID + ",b," + h2 + "," + word

