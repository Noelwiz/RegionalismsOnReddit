#idea: just make the document a list of words
#header has just a # for the total non-stop word
#%s for the word _space_ %d the number of occurences
from nltk import FreqDist
from nltk.util import bigrams
from UtilityFunctions import readRegionalisms, readSubredditSet, getTextFileNames


processeddatadirectory = "../../data/ProcessedData"


def bigramFreqFile(subreddit):
    #get filtered files
    filenames = getTextFileNames(subreddit)
    countfilename = processeddatadirectory + "/count_bigram_"+subreddit+".txt"
    countVectorFile = open(countfilename, "a+",
                    errors='ignore')
    frequencies = FreqDist()

    #good canidate for multithreading. one thread for file, each with own freq dist, combo after all finish.
    for filename in filenames:
        print("sending normalized values of " + filename + " to " + countfilename)
        with open(filename, "r", errors="ignore") as current_file:
            for line in current_file:
                for bigram in list(bigrams(line.split())):
                    if len(bigram[0]) < 36 and len(bigram[1] < 36) and bigram[1] != "<end_comment>":
                        frequencies[bigram] = frequencies.get(bigram, 0) + 1

    #write total number of words
    countVectorFile.write(str(frequencies.N()))

    #note, another good improvement, organize this for faster searching.
    for bigram, count in frequencies:
        countVectorFile.write(" ".join(bigram)+" "+str(count))

    countVectorFile.close()



def unigramFreqFile(subreddit):
    # get filtered files
    filenames = getTextFileNames(subreddit)
    countFileName = processeddatadirectory + "/count_unigram_" + subreddit + ".txt"
    countVectorFile = open(countFileName, "a+", errors='ignore')
    frequencies = FreqDist()

    for filename in filenames:
        print("sending normalized values of " + filename + " to " + countFileName)
        with open(filename, "r", errors="ignore") as current_file:
            for line in current_file:
                for word in line.split():
                    word = word.strip()
                    if len(word) < 36:
                        frequencies[word] = frequencies.get(word, 0) + 1

    frequencies["<end_comment>"] = 0
    # write total number of words
    countVectorFile.write(str(frequencies.N()))
    for word, count in frequencies:
        countVectorFile.write(word+" "+str(count))

    countVectorFile.close()




def main():
    readRegionalisms()
    toProcess = readSubredditSet()

    #another good canidate for multithreading
    for subreddit in toProcess:
        unigramFreqFile(subreddit)
        bigramFreqFile(subreddit)


if __name__ == "__main__":
    main()
