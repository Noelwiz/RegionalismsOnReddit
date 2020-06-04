import nltk
from nltk import FreqDist
import convokit
from convokit import Corpus, download, FightingWords
import re
import string
import os
import csv
import math
from os import path

import DataProcessing
from DataProcessing import ProcessToText
# https://convokit.cornell.edu/documentation/data_format.html
from DataProcessing.ProcessToText import readRegionalisms
from UtilityFunctions import getTextFileNames, readSubredditSet, getRegionalisms

datadirectory = "../../data"


###############################################
#### analyze - audience
###############################################
def checkComment(comment):
    line = comment.split()
    has_regionalism = False

    regionalisms = getRegionalisms()

    for word in line:
        if word in regionalisms:
            has_regionalism = True
            break
    return has_regionalism


def collectAudienceFreqData(file_name):
    numcomments = 0
    numcommentswithregionalism = 0
    with open(file_name, "r") as current_file:
        # https://waymoot.org/home/python_string/
        # should be credited for this odd joining method
        current_comment = []
        print("reading lines")
        for line in current_file:
            c_partition = line.partition("<end_comment>")
            current_comment.append(c_partition[0])

            if len(c_partition) > 0:
                numcomments = numcomments + 1
                comment = ''.join(current_comment)
                if checkComment(comment):
                    numcommentswithregionalism = numcommentswithregionalism + 1
                current_comment = []

    return numcommentswithregionalism, numcomments


def recordAudienceData(corpusname, csvwritter):
    towrite = [corpusname]
    for file in getTextFileNames(corpusname, filtered=True):
        print("recording the file: " + file)
        if path.exists(file):
            comment_with, numcomments = collectAudienceFreqData(file)
            print("num comment: " + str(numcomments))
            print("num w/ thing: " + str(comment_with))
            freq = round(comment_with / numcomments, 5)
            towrite.append(freq)
        else:
            print("no such file: " + file)
            towrite.append(0)
    csvwritter.writerow(towrite)


def analyzeAudienceData(corpuslist, outfilename="results_audience"):
    datafilepath = datadirectory + "/results/" + outfilename + ".csv"
    if not path.exists(datafilepath):
        # create an empty file
        open(datafilepath, "x").close()
        csvfile = open(datafilepath, "a", newline='')
        csvwriter = csv.writer(csvfile, dialect='excel')

        # see getUnfilteredTextFilename for order
        csvwriter.writerow(["Subreddit", "Post", "Post with Mention", "Comment ", "Comment with Mention"])
    else:
        csvfile = open(datafilepath, "a", newline='')
        csvwriter = csv.writer(csvfile, dialect='excel')

    for corpus_name in corpuslist:
        files = getTextFileNames(corpus_name)
        recordAudienceData(corpus_name, csvwriter)
    csvfile.close()


###############################################
#### analyze - frequency
###############################################

def collectFreqData(file_name):
    fqdist = FreqDist()
    with open(file_name, "r") as current_file:
        for line in current_file:
            for word in line.split():
                fqdist[word] = fqdist.get(word, 0) + 1
    return fqdist


def recordFrequencyData(corpusname, csvwritter, useLogFreq=False):
    totalFQ = FreqDist()
    processed_corpus_texts = getTextFileNames(corpusname)

    for file in processed_corpus_texts:
        print("recording the file: " + file)
        if path.exists(file):
            freqs = collectFreqData(file)
            totalFQ = mergeFreqDist(freqs, totalFQ)

    towrite = dict()
    towrite["Subreddit"] = corpusname

    for word in getRegionalisms():
        if totalFQ[word] == 0:
            towrite[word] = 0
        else:
            if useLogFreq:
                towrite[word] = math.log(totalFQ[word] / totalFQ.N())
            else:
                towrite[word] = totalFQ[word] / totalFQ.N()
    csvwritter.writerow(towrite)


def analyzeFrequencyData(corpuslist, outfilename="results_frequencys"):
    datafilepath = datadirectory + "/results/" + outfilename + ".csv"
    fieldnames = ["Subreddit"]

    for word in getRegionalisms():
        fieldnames.append(word)
    print(fieldnames)

    if not path.exists(datafilepath):
        # create an empty file
        open(datafilepath, "x").close()
        csvfile = open(datafilepath, "a", newline='')
        csvwriter = csv.DictWriter(csvfile, fieldnames, restval=0, dialect='excel')
        csvwriter.writeheader()

    else:
        csvfile = open(datafilepath, "a", newline='')
        csvwriter = csv.DictWriter(csvfile, fieldnames, restval=0, dialect='excel')

    for corpus in corpuslist:
        recordFrequencyData(corpus, csvwriter)
    csvfile.close()

###############################################
#### Counting Regionalisms
###############################################

def recordCountData(corpusname, csvwritter):
    totalFQ = FreqDist()
    processed_corpus_texts = getTextFileNames(corpusname)

    for file in processed_corpus_texts:
        print("recording the file: " + file)
        if path.exists(file):
            freqs = collectFreqData(file)
            totalFQ = mergeFreqDist(freqs, totalFQ)

    towrite = dict()
    towrite["Subreddit"] = corpusname

    for word in getRegionalisms():
        towrite[word] = totalFQ[word]

    csvwritter.writerow(towrite)


def analyzeCountData(corpuslist, outfilename="results_counts"):
    datafilepath = datadirectory + "/results/" + outfilename + ".csv"
    fieldnames = ["Subreddit"]

    for word in getRegionalisms():
        fieldnames.append(word)
    print(fieldnames)

    if not path.exists(datafilepath):
        # create an empty file
        open(datafilepath, "x").close()
        csvfile = open(datafilepath, "a", newline='')
        csvwriter = csv.DictWriter(csvfile, fieldnames, restval=0, dialect='excel')
        csvwriter.writeheader()

    else:
        csvfile = open(datafilepath, "a", newline='')
        csvwriter = csv.DictWriter(csvfile, fieldnames, restval=0, dialect='excel')

    for corpus in corpuslist:
        recordCountData(corpus, csvwriter)
    csvfile.close()

###############################################
#### stats
###############################################
def mergeFreqDist(fq1, fq2):
    combigned = fq1.copy()
    allkeys = set(combigned.keys())
    allkeys.union(set(fq2.keys()))
    for word in allkeys:
        combigned[word] = (fq2.get(word, 0) + combigned.get(word, 0))
    return combigned


def recordStatsData(corpusname, csvwritter):
    totalFQ = FreqDist()
    processed_corpus_texts = getTextFileNames(corpusname, filtered=False)

    numcomments_pnm = 0
    numcomments_pm = 0
    numcomments_cm = 0
    numcomments_cnm = 0

    # post no mention
    if path.exists(processed_corpus_texts[0]):
        print("reading: " + processed_corpus_texts[0])
        freqs_pnm = collectFreqData(processed_corpus_texts[0])
        totalFQ = mergeFreqDist(totalFQ, freqs_pnm)
        junk, numcomments_pnm = collectAudienceFreqData(processed_corpus_texts[0])
    # post mention
    if path.exists(processed_corpus_texts[1]):
        print("reading: " + processed_corpus_texts[1])
        freqs_pm = collectFreqData(processed_corpus_texts[1])
        totalFQ = mergeFreqDist(totalFQ, freqs_pm)
        junk, numcomments_pm = collectAudienceFreqData(processed_corpus_texts[1])
    # comment no mention
    if path.exists(processed_corpus_texts[2]):
        print("reading: " + processed_corpus_texts[2])
        freqs_cnm = collectFreqData(processed_corpus_texts[2])
        totalFQ = mergeFreqDist(totalFQ, freqs_cnm)
        junk, numcomments_cnm = collectAudienceFreqData(processed_corpus_texts[2])
    # comment mention
    if path.exists(processed_corpus_texts[3]):
        print("reading: " + processed_corpus_texts[3])
        freqs_cm = collectFreqData(processed_corpus_texts[3])
        totalFQ = mergeFreqDist(totalFQ, freqs_cm)
        junk, numcomments_cm = collectAudienceFreqData(processed_corpus_texts[3])

    print("writing")

    towrite = dict()
    towrite["Subreddit"] = corpusname
    towrite["N"] = totalFQ.N()
    towrite["B"] = totalFQ.B()
    towrite["Num Utterences"] = numcomments_pnm + numcomments_pm + numcomments_cm + numcomments_cnm
    towrite["Num Utterences - Post NM"] = numcomments_pnm
    towrite["Num Utterences - Post M"] = numcomments_pm
    towrite["Num Utterences - Comment"] = numcomments_cnm
    towrite["Num Utterences - Comment M"] = numcomments_cm

    if path.exists(processed_corpus_texts[0]):
        towrite["N-Post"] = freqs_pnm.N()
        towrite["B-Post"] = freqs_pnm.B()
    else:
        towrite["N-Post"] = 0
        towrite["B-Post"] = 0

    if path.exists(processed_corpus_texts[1]):
        towrite["N-Post with Mention"] = freqs_pm.N()
        towrite["B-Post with Mention"] = freqs_pm.B()
    else:
        towrite["N-Post with Mention"] = 0
        towrite["B-Post with Mention"] = 0

    if path.exists(processed_corpus_texts[2]):
        towrite["N -Comment"] = freqs_cnm.N()
        towrite["B -Comment"] = freqs_cnm.B()
    else:
        towrite["N -Comment"] = 0
        towrite["B -Comment"] = 0

    if path.exists(processed_corpus_texts[3]):
        towrite["N -Comment with Mention"] = freqs_cm.N()
        towrite["B -Comment with Mention"] = freqs_cm.B()
    else:
        towrite["N -Comment with Mention"] = 0
        towrite["B -Comment with Mention"] = 0
    csvwritter.writerow(towrite)


def analyzeStatsData(corpuslist, outfilename="results_stats"):
    datafilepath = datadirectory + "/results/" + outfilename + ".csv"
    fieldnames = ["Subreddit", "N", "B", "Num Utterences",
                  "N-Post", "B-Post", "Num Utterences - Post NM",
                  "N-Post with Mention", "B-Post with Mention", "Num Utterences - Post M",
                  "N -Comment", "B -Comment", "Num Utterences - Comment",
                  "N -Comment with Mention", "B -Comment with Mention", "Num Utterences - Comment M", ]
    if not path.exists(datafilepath):
        # create an empty file
        open(datafilepath, "x").close()
        csvfile = open(datafilepath, "a", newline='')
        csvwriter = csv.DictWriter(csvfile, fieldnames, restval=0, dialect='excel')
        csvwriter.writeheader()

    else:
        csvfile = open(datafilepath, "a", newline='')
        csvwriter = csv.DictWriter(csvfile, fieldnames, restval=0, dialect='excel')

    for corpus in corpuslist:
        recordStatsData(corpus, csvwriter)
    csvfile.close()


###############################################
#### main
###############################################
def main():
    readRegionalisms()
    # to select subreddits to process, add their name to the CurrentSubredditSet file
    toAnalyze = readSubredditSet()
    print(toAnalyze)
    analyzeAudienceData(toAnalyze)
    analyzeFrequencyData(toAnalyze)
    analyzeStatsData(toAnalyze)
    analyzeCountData(toAnalyze)


if __name__ == "__main__":
    main()
