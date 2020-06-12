import csv
from os import path

from nltk import FreqDist

from Regionalisms_analysis.Analyze import collectFreqData
from UtilityFunctions import readRegionalisms, readSubredditSet, getTextFileNames, getRegionalisms, \
    initalizeFreqDistWithKeys
import math


datadirectory = "../../data"


def getUniqueWords(subredditname):
    wordfile_path = datadirectory + "/ProcessedData/" + subredditname+"_words" + ".txt"

    set_of_words = set()
    freq_subreddit = FreqDist()

    if not path.exists(wordfile_path):
        for datafile in getTextFileNames(subredditname):
            if path.exists(datafile):
                print("reading " + datafile)
                freq_subreddit = collectFreqData(datafile) + freq_subreddit
            else:
                print("no data for "+datafile)

        for i in freq_subreddit.most_common(20):
            print(i)

        with open(wordfile_path, "a+") as wordfile:
            for word in freq_subreddit.keys():
                word = word.strip()
                word = word.lower()
                set_of_words.add(word)
                wordfile.write(word + "\n")
        return set_of_words
    else:
        with open(wordfile_path, "r") as wordfile:
            #read line by line
            print("reading "+ wordfile_path)
            for word in wordfile:
                word = word.strip()
                word = word.lower()
                set_of_words.add(word)
            return set_of_words
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
    print("There are "+ str(len(docFreqDistros))+" documents. ")

    idfDict = dict.fromkeys(allwords,0)
    for distro in docFreqDistros:
        for word in distro.keys():
            word = word.lower().strip() #should be unessiccary
            if distro.get(word, 0) > 0:
                idfDict[word] = idfDict.get(word, 0) + 1

    for word, value in idfDict.items():
        idfDict[word] = math.log(N/float(value))
    return idfDict


#https://towardsdatascience.com/natural-language-processing-feature-engineering-using-tf-idf-e8b9d00e7e76
def computeTFIDF(wordfreqs, idfscores, allwords):
    tfidf_scores = dict().fromkeys(allwords,0)

    for word in wordfreqs.keys():
        tfidf_scores[word] = wordfreqs.get(word, 0)*idfscores.get(word,0)
    return  tfidf_scores


def recordAllTFIDF(tfidfscore, subredditname, fieldnames, outfilename="all_tfidfscores" ,prefix=""):
    if len(prefix) > 0 :
        datafilepath = datadirectory + "/results/" + prefix + outfilename + ".csv"
    else:
        datafilepath = datadirectory + "/results/" + outfilename + ".csv"

    tfidfscore = tfidfscore.copy()
    tfidfscore["Subreddit"] = subredditname


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


def recordRegionalismTFIDF(tfidfscore, subredditname, fieldnames, outfilename="regionalism_tfidfscores" ,prefix=""):
    if len(prefix) > 0 :
        datafilepath = datadirectory + "/results/" + prefix + outfilename + ".csv"
    else:
        datafilepath = datadirectory + "/results/" + outfilename + ".csv"

    print("recording tf-idf scores in "+datafilepath)

    towrite = dict()
    towrite["Subreddit"] = subredditname

    for word in fieldnames:
        towrite[word] = tfidfscore.get(word, 0)

    if not path.exists(datafilepath):
        # create an empty file
        open(datafilepath, "x").close()
        csvfile = open(datafilepath, "a", newline='')
        csvwriter = csv.DictWriter(csvfile, fieldnames, restval=0, dialect='excel')
        csvwriter.writeheader()

    else:
        csvfile = open(datafilepath, "a", newline='')
        csvwriter = csv.DictWriter(csvfile, fieldnames, restval=0, dialect='excel')

    csvwriter.writerow(towrite)
    csvfile.close()


def getRegionalismsOnlyCSVKeys():
    fieldnames = ["Subreddit"]
    fieldnames.extend(getRegionalisms())
    return  fieldnames

def getAllWordCSVKeys(allWords):
    fieldnames = ["Subreddit"]
    fieldnames = fieldnames.extend(allWords)
    return fieldnames

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
        allwords = allwords.union(getUniqueWords(subreddit))
        print(subreddit+" added "+str(len(allwords) - numprevwords)+" words.")

    print("in total, there are " + str(len(allwords)) + " words in the vector.")


    frequenceylist = list()
    for subreddit in toAnalyze:
        currentfreq = initalizeFreqDistWithKeys(allwords)
        print("num keys in frequency: "+str(len(currentfreq.keys())))
        for file in getTextFileNames(subreddit):
            currentfreq = collectFreqData(file) + currentfreq
        frequenceylist.append(currentfreq)

        print("currently, there are "+str(len(currentfreq.keys())) + "unique words in "+subreddit)

    idf_scores = computeIDF(frequenceylist, allwords)

    tfidf_scores = list()

    #problem, don't know what goes with what.
    for frequency in frequenceylist:
        tfidf_scores.append(computeTFIDF(frequency, idf_scores, allwords))


    csv_keys = getRegionalismsOnlyCSVKeys()
    #csv_keys = getAllWordCSVKeys(allwords)

    for i in range(len(toAnalyze)):
        recordRegionalismTFIDF(tfidf_scores[i], toAnalyze[i], csv_keys)
        #recordAllTFIDF(tfidf_scores[i], toAnalyze[i], csv_keys)

if __name__ == "__main__":
    main()
