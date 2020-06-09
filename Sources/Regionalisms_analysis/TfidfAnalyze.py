import csv
from os import path

from nltk import FreqDist

from Regionalisms_analysis.Analyze import collectFreqData
from UtilityFunctions import readRegionalisms, readSubredditSet, getTextFileNames, getRegionalisms, \
    initalizeFreqDistWithKeys
import math


datadirectory = "../../data"


def getUniqueWords(subredditname):
    datafilepath = datadirectory + "/ProcessedData/" + subredditname+"_words" + ".txt"

    words = set()
    subredditFreq = FreqDist()

    if not path.exists(datafilepath):
        for datafile in getTextFileNames(subredditname):
            if path.exists(datafile):
                print("reading " + datafile)
                subredditFreq = collectFreqData(subredditname) + subredditFreq
            else:
                print("no data for "+datafile)
        words = subredditFreq.keys()
        for i in subredditFreq.most_common(20):
            print(i)

        with open(datafilepath, "a+") as wordfile:
            for word in words:
                word.strip()
                word.lower()
                wordfile.write(word + "\n")
    else:
        with open(datafilepath, "r") as wordfile:
            #read line by line
            print("reading "+ datafilepath)
            for word in wordfile:
                word.strip()
                word.lower()
                words.add(word)

    return  words
###############################################
#### tf-idf
###############################################
## 1) make freq Distro for all words in documents
## 1.5) if time, also add bigrams
## 2) compute word frequencies for all documents
## 3) compute IDF scores for all words in documents
## 4) compute TF-IDF scores for words
## 5) do analysis.
##
## also: might be able to use the recorded

def computeIDF(docFreqDistros, allwords): #todo: args
    # https://towardsdatascience.com/natural-language-processing-feature-engineering-using-tf-idf-e8b9d00e7e76

    """in: list of frequency distros by subreddit, out: IDF for all words that are keys"""
    N = len(docFreqDistros)

    idfDict = dict.fromkeys(allwords,0)
    for distro in docFreqDistros:
        for word in idfDict.keys():
            if distro.get(word, 0):
                idfDict[word] += 1

    for word in idfDict.keys():
        idfDict[word] = math.log(N/float(idfDict.get(word)))
    return idfDict


#https://towardsdatascience.com/natural-language-processing-feature-engineering-using-tf-idf-e8b9d00e7e76
def computeTFIDF(wordfreqs, idfscores):
    tfidf_scores = dict()

    for word in wordfreqs.keys():
        if idfscores.get(word, 0) == 0:
            print("warning: no entries in idf scores for "+word)
        tfidf_scores[word] = wordfreqs.get(word, 0)*idfscores.get(word,0)
    return  tfidf_scores


def recordAllTFIDF(tfidfscore, subredditname, outfilename="all_tfidfscores" ,prefix=""):
    if len(prefix) > 0 :
        datafilepath = datadirectory + "/results/" + prefix + outfilename + ".csv"
    else:
        datafilepath = datadirectory + "/results/" + outfilename + ".csv"

    tfidfscore = tfidfscore.copy()
    tfidfscore["Subreddit"] = subredditname
    fieldnames= ["Subreddit"]
    fieldnames.extend(tfidfscore.keys())

    if not path.exists(datafilepath):
        # create an empty file
        open(datafilepath, "x").close()
        csvfile = open(datafilepath, "a", newline='')
        csvwriter = csv.DictWriter(csvfile, fieldnames, restval=0, dialect='excel')
        csvwriter.writeheader()

    else:
        csvfile = open(datafilepath, "a", newline='')
        csvwriter = csv.DictWriter(csvfile, fieldnames, restval=0, dialect='excel')

    csvwriter.writerow(tfidfscore)
    csvfile.close()


def recordRegionalismTFIDF(tfidfscore, subredditname, outfilename="regionalism_tfidfscores" ,prefix=""):
    if len(prefix) > 0 :
        datafilepath = datadirectory + "/results/" + prefix + outfilename + ".csv"
    else:
        datafilepath = datadirectory + "/results/" + outfilename + ".csv"

    tfidfscore = tfidfscore.copy()
    tfidfscore["Subreddit"] = subredditname
    fieldnames= ["Subreddit"]
    fieldnames.extend(getRegionalisms().keys())

    if not path.exists(datafilepath):
        # create an empty file
        open(datafilepath, "x").close()
        csvfile = open(datafilepath, "a", newline='')
        csvwriter = csv.DictWriter(csvfile, fieldnames, restval=0, dialect='excel')
        csvwriter.writeheader()

    else:
        csvfile = open(datafilepath, "a", newline='')
        csvwriter = csv.DictWriter(csvfile, fieldnames, restval=0, dialect='excel')

    csvwriter.writerow(tfidfscore)
    csvfile.close()

###############################################
#### main
###############################################
def main(prefix=""):
    readRegionalisms()
    # to select subreddits to process, add their name to the CurrentSubredditSet file
    #NOTE: actually returns a list.
    toAnalyze = readSubredditSet()
    print(toAnalyze)

    allwords = getRegionalisms().copy()
    for subreddit in toAnalyze:
        numprevwords = len(allwords)
        print("num unique words: "+str(numprevwords))
        allwords.union(getUniqueWords(subreddit))
        print(subreddit+" added "+str(len(allwords) - numprevwords)+" words.")

    print("in total, there are " + str(len(allwords)) + " words in the vector.")


    frequenceylist = list()
    for subreddit in toAnalyze:
        currentfreq = initalizeFreqDistWithKeys(allwords)
        for file in getTextFileNames(subreddit):
            currentfreq += collectFreqData(file)
        frequenceylist.append(currentfreq)

    idf_scores = computeIDF(frequenceylist, allwords)

    tfidf_scores = list()

    #problem, don't know what goes with what.
    for frequency in frequenceylist:
        tfidf_scores.append(computeTFIDF(frequency, idf_scores))


    for i in range(len(toAnalyze)):
        recordRegionalismTFIDF(tfidf_scores[i], toAnalyze[i])

if __name__ == "__main__":
    main(prefix="fur")
