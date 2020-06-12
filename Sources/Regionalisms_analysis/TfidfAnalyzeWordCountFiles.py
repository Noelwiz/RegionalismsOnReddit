#psudocode
# 1) load up frequencies from desired subreddit set
# 1.5) chose words to look at
# 2) calulate idf scores for words
# 2.5) maybe use regionalisms to set up a good range
# 3) save a list of words within a range
import csv

from nltk import FreqDist
from os import path

from Regionalisms_analysis.AltTfidfAnalyze import calculateIDF
from UtilityFunctions import readRegionalisms, readSubredditSet, getCountFileName, getRegionalisms

datafolder = "../../data"


#take a subreddit name and rebuild the frequency distro
def getFrequency(subredditname, unigram=True):
    fqdist = FreqDist()
    filename = getCountFileName(subredditname, unigram=unigram)
    with open(filename, "r") as counts:
        #skip first line with N value
        counts.readline()
        for line in counts:
            line = line.split()
            fqdist[line[0]] = int(line[1])
    return fqdist


def calcTfidf(subdata, wordset, idfscores):
    TfidfDict = dict().fromkeys(wordset, 0)
    for word in wordset:
        TfidfDict[word] = float(subdata.freq(word)) * float(idfscores[word])

    return  TfidfDict


def chooseScoreRange(tfidf_scores):
    # regionalisms = getRegionalisms()
    # mydict = dict()
    # for word in regionalisms:
    #     mydict[word] = tfidf_scores.get(word,0)
    #
    # regionalism_set = set()
    # canidate_set = set()
    # for word in mydict.keys():
    #     if mydict[word] != 0:
    #         canidate_set.add(word)
    #
    # #TODO: figure out how to choose this
    # max = 0
    # min = 0

    #min, max
    #0.0000362067197637493
    return (0.00001, 0.0001)



#1 2 4 5
def outputResults(tfidf, score_range=(0.000004,0.00007), prefix=" "):
    subredditname = tfidf[0]
    scores =tfidf[1]
    regionalisms = getRegionalisms()

    output = dict()
    output["Subreddit"] = subredditname

    words = set()
    for word in scores:
        if score_range[0] < scores.get(word,0) < score_range[1]:
            words.add(word)
            output[word] = scores[word]

        if word in regionalisms and scores[word] > 0:
            print(subredditname + " has " + word + " with score " + str(scores[word]))


    #check if prefix should be included
    if len(prefix) > 1:
        datafilepath = datafolder + "/results/"+ prefix+ subredditname +"_results_tfidf.csv"
    else:
        datafilepath = datafolder + "/results/" + subredditname + "_results_tfidf.csv"

    if not path.exists(datafilepath):
        open(datafilepath, "x").close()

    with open(datafilepath, "a+", newline='') as csvfile:
        fieldnames = list()
        fieldnames.append("Subreddit")
        fieldnames.extend(words)
        csvwriter = csv.DictWriter(csvfile, fieldnames, dialect='excel')
        csvwriter.writeheader()
        csvwriter.writerow(output)



def main():
    print("doing stuff")
    readRegionalisms()
    #because sets aren't in a stable ordering,
    # and calculateIDF expects just a freqdist not a (sub name, freqdist) tuple
    toProcess = list(readSubredditSet())
    frequencies = list()
    for subredditname in toProcess:
        #todo: figure out how to also do bigrams.
        c_freqdist = getFrequency(subredditname)
        frequencies.append(c_freqdist)

    #now have a list of all words
    totalfreq = FreqDist()
    for frequency in frequencies:
        totalfreq = frequency + totalfreq


    #get list of words to calculate tf-idf score for
    N = len(frequencies)
    all_words = set(totalfreq.keys())
    #remove all words that only occcur on average less than once per corpus.
    #based on http://www.nltk.org/_modules/nltk/probability.html#FreqDist.hapaxes
    all_words = all_words - {item for item in totalfreq.keys() if totalfreq[item] < N}

    rnrdict = totalfreq.r_Nr()
    numremoved = 0
    for i in range(N):
        numremoved += rnrdict.get(i, 0)

    print("removed "+str(numremoved)+" words from the set of words processed due to low frequency.")
    del rnrdict, numremoved

    idfdict = dict()
    for word in all_words:
        #calculate idf scores for words
        idfdict[word] = calculateIDF(frequencies, word, len(toProcess))

    #frequencies are in the freq dist, idf of a word is in idfdict. now onto like ???
    #tfidf = list()
    for i in range(len(toProcess)):
        current = (toProcess[i], calcTfidf(frequencies[i], all_words, idfdict) )
        outputResults(current)
        #tfidf.append(current)


if __name__ == "__main__":
    main()