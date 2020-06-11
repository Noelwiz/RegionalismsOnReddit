from nltk import FreqDist

regionalisms = set()
datadirectory = "../../data"

def getRegionalisms():
    if len(regionalisms) > 1:
        return regionalisms
    else:
        readRegionalisms()
        return regionalisms


def readSubredditSet():
    with open(datadirectory + "/CurrentSubredditSet.txt", "r") as subredditfiles:
        subreddits = list()
        for subreddit in subredditfiles.readlines():
            if not subreddit.startswith("#") and len(subreddit) > 1:
                subreddits.append(subreddit.strip())
    return subreddits


###############################################
#### derive file names
###############################################
def getTextFileNames(corpusname, filtered=True):
    outputBasefilename = datadirectory + "/ProcessedData/" + corpusname
    filenames = [outputBasefilename + "_cmt_nomention.txt",
                 outputBasefilename + "_cmt_mention.txt",
                 outputBasefilename + "_pst_nomention.txt",
                 outputBasefilename + "_pst_mention.txt"]

    if filtered:
        unfilteredFileNames = filenames.copy()
        filenames = []
        for c_filename in unfilteredFileNames:
            nameinsert_index = c_filename.rfind("/")
            filenames.append(c_filename[:nameinsert_index + 1] + "filtered_" + c_filename[nameinsert_index + 1:])
    return filenames



def readRegionalisms():
    regionalisms_file = open("../../data/regionalisms.txt", "r+")
    for word in regionalisms_file.readlines():
        regionalisms.add(word.strip().lower())
    regionalisms_file.close()


def initalizeFreqDistWithKeys(keys, smoothinglambda=0):
    fqdist = FreqDist()

    for key in keys:
        fqdist[key] = smoothinglambda

    return  fqdist