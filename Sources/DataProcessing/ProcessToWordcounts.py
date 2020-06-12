#idea: just make the document a list of words
#header has just a # for the total non-stop word
#%s for the word _space_ %d the number of occurences
from nltk import FreqDist
from nltk.util import bigrams
from os import path
from UtilityFunctions import readRegionalisms, readSubredditSet, getTextFileNames, getCountFileName

processeddatadirectory = "../../data/ProcessedData"


def bigramFreqFile(subreddit):
    #get filtered files
    filenames = getTextFileNames(subreddit)
    countfilename = getCountFileName(subreddit, unigram=False)
    with open(countfilename, "a+", errors='ignore') as countVectorFile:
        frequencies = FreqDist()

        #good canidate for multithreading. one thread for file, each with own freq dist, combo after all finish.
        for filename in filenames:
            print("sending normalized values of " + filename + " to " + countfilename)
            with open(filename, "r", errors="ignore") as current_file:
                for line in current_file:
                    for bigram in list(bigrams(line.split())):
                        okayrange = 0 < len(bigram[0])  < 23 and 0 < len(bigram[1]) < 23
                        if okayrange and bigram[1] != "<end_comment>":
                            frequencies[bigram] = frequencies.get(bigram, 0) + 1

        #write total number of words
        countVectorFile.write(str(frequencies.N()))

        #note, another good improvement, organize this for faster searching.
        for bigram in frequencies:
            countVectorFile.write(" ".join(bigram)+" "+str(frequencies[bigram]))



def unigramFreqFile(subreddit):
    # get filtered files
    filenames = getTextFileNames(subreddit)
    countFileName = getCountFileName(subreddit)
    with open(countFileName, "a+", errors='ignore') as countVectorFile:
        frequencies = FreqDist()
        for filename in filenames:
            print("sending normalized values of " + filename + " to " + countFileName)
            with open(filename, "r", errors="ignore") as current_file:
                for line in current_file:
                    for word in line.split():
                        word = word.strip()
                        if word.startswith("http") or word.isnumeric():
                            continue
                        if 0 < len(word) < 23:
                            frequencies[word] = frequencies.get(word, 0) + 1

        frequencies["<end_comment>"] = 0
        # write total number of words
        countVectorFile.write(str(frequencies.N()))
        for word in frequencies:
            countVectorFile.write(word+" "+str(frequencies[word])+"\n")





def main(doBigram=False):
    readRegionalisms()
    toProcess = readSubredditSet()

    #another good canidate for multithreading
    for subreddit in toProcess:
        if not path.exists(getCountFileName(subreddit)):
            unigramFreqFile(subreddit)
        #bigram was causing a memory error, so default is not to run this on bigrams
        if doBigram and not path.exists(getCountFileName(subreddit, unigram=False)):
            bigramFreqFile(subreddit)


if __name__ == "__main__":
    main()
