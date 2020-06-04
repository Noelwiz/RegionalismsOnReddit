import os
from zipfile import ZipFile

from convokit import Corpus, download

from nltk.corpus import stopwords
import convokit.util
import json
import re
from os import path

datadirectory = "../../data"
user_pattern = re.compile("/u/")
ufile = "utterances.jsonl"
ufilelen = len(ufile)

stopwords = set(stopwords.words('english'))
regionalisms = set()


###############################################
#### derive file names
###############################################
def getTextFileNames(corpusname, filtered=True):
    outputBasefilename = datadirectory+"/ProcessedData/" + corpusname
    filenames = [outputBasefilename + "_cmt_nomention.txt",
            outputBasefilename + "_cmt_mention.txt",
            outputBasefilename + "_pst_nomention.txt",
            outputBasefilename + "_pst_mention.txt"]

    if(filtered):
        unfilteredFileNames = filenames.copy()
        filenames = []
        for c_filename in unfilteredFileNames:
            nameinsert_index = c_filename.rfind("/")
            filenames.append(c_filename[:nameinsert_index+1] + "filtered_" + c_filename[nameinsert_index+1:])
    return filenames



###############################################
#### catagorize
###############################################
def mentionsUser(comment):
    #if it includes "/u/"
    if(None == user_pattern.search(comment)):
        return False
    else:
        return True

###############################################
#### stopword removal
###############################################
def addStopWords(extrastopfile="../../data/supplementalremovedwords.txt"):
    global stopwords
    readRegionalisms()

    extrastopfile = open(extrastopfile, "r+")
    extrastopfile_text = extrastopfile.read()
    extrastopfile.close()
    # filter out regionalims from the stop words
    stopwords.union(set(extrastopfile_text.split()))

    local_copy = regionalisms.copy()

    #avoid filtering out part of a regionalism if it's two words
    for word in local_copy:
        local_copy.union(set(word.split()))
        
    stopwords.difference_update(regionalisms)


def readRegionalisms():
    regionalisms_file = open("../../data/regionalisms.txt", "r+")
    for word in regionalisms_file.readlines():
        regionalisms.add(word)
    regionalisms_file.close()

    

def removestopwords(filename):
    global stopwords
    if(stopwords == None):
        stopwords = set(stopwords.words('english'))
        addStopWords()
        
    nameinsert_index = filename.rfind("/")
    print("sending normalized values of " + filename + " to "+ filename[:nameinsert_index+1] + "filtered_" + filename[nameinsert_index+1:])
    filtered = open(filename[:nameinsert_index+1] + "filtered_" + filename[nameinsert_index+1:], "a+",  errors='ignore')

    with open(filename, "r") as current_file:
        for line in current_file.readlines():
            if(len(line) > 0 and line != "[deleted] <end_comment>"):
                ##hopefully not a new line
                line = line.split()
                for word in line:
                    if not word in stopwords:
                        filtered.write(word+" ", )
                filtered.write("\n")

    filtered.close()


###############################################
#### Process to Textfile
###############################################
def convertToText(corpusname, downcase=True, includebots=False, keepStickied=True):
    """
    convert a corpus, assuming the .utterences file has been extracted, to 4 text files
    :param corpusname:
    :param downcase:
    :return:
    """
    with open(datadirectory+"/ProcessedData/"+corpusname+"/utterances.jsonl", "r", errors='ignore', encoding="'utf-8'") as corpus_file:
        for jsonline in corpus_file.readlines():
            current = json.loads(jsonline)
            comment = current["text"]

            #normalize
            if(downcase):
                comment = comment.lower()
            comment = comment.strip()

            #check if mentions user
            mention = mentionsUser(comment)
            metadata = current["meta"]
            ispost = (None == metadata["top_level_comment"])

            if(not includebots):
                isbot = False

                #check if automod
                isAutomod = current["user"] == "AutoMod"
                isbot = isbot and not isAutomod

                #checkifbot
                flare = metadata.get("author_flair_text")
                if(len(flare) > 0):
                    flare = flare.lower()
                    if(flare.endswith("bot")):
                        isbot = True

                if(isbot):
                    continue


            if not keepStickied:
                #check if stickied
                if(metadata.get("stickied")):
                    continue


            #catagorize
            if(ispost):
                if(mention):
                    #post and mention
                    textfile = open(datadirectory+"/ProcessedData/" + corpusname+"_pst_mention.txt", "a+", errors='ignore')
                else:
                    #post no mention
                    textfile = open(datadirectory+"/ProcessedData/" + corpusname+"_pst_nomention.txt", "a+", errors='ignore')
            else:
                if(mention):
                    #not most yes mention
                    textfile = open(datadirectory+"/ProcessedData/" + corpusname+"_cmt_mention.txt", "a+",  errors='ignore')
                else:
                    #no post no mention
                    textfile = open(datadirectory+"/ProcessedData/" + corpusname+"_cmt_nomention.txt", "a+",  errors='ignore')
            #save to text file
            textfile.write(comment+" <end_comment>\n")
            textfile.close()


#re-process text files to adjust stopword removal
def removeStopwordsFromConverted(corpusname):
    for file in getTextFileNames(corpusname, filtered=False):
        if(path.exists(file)):
            removestopwords(file)
    return
    


def main():
    #initalize globals
    readRegionalisms()
    addStopWords()

    toProcess = ["furry_irl", "furry", "yiff"]
    for corpusname in toProcess:
        print("doing, "+corpusname)
        download("subreddit-"+corpusname, data_dir=datadirectory+"/DataDownloads")

        #create the directory
        if not os.path.exists(datadirectory+"/ProcessedData/"+corpusname):
            os.makedirs(datadirectory+"/ProcessedData/"+corpusname)

        with ZipFile(datadirectory+"/DataDownloads/"+corpusname+".corpus.zip", mode="r") as corpuszip:
            if not os.path.exists(datadirectory+"/ProcessedData/"+corpusname+"/utterances.jsonl"):
                corpuszip.extract("utterances.jsonl", path=datadirectory+"/ProcessedData/"+corpusname+"/")


        #make the unfilted text files
        old_data_exists = False
        for file in getTextFileNames(corpusname, filtered=False):
            if(os.path.exists(file)):
                old_data_exists = True

        if not old_data_exists:
            convertToText(corpusname)
        else:
            print(corpusname + " has already been converted to unfiltered text files, moving on")

        # remove stopwords
        old_data_exists = False
        for file in getTextFileNames(corpusname):
            if(os.path.exists(file)):
                old_data_exists = True

        if not old_data_exists:
            removeStopwordsFromConverted(corpusname)
        else:
            print(corpusname + " has already had its text files filtered")
        
        
if __name__ == "__main__":
    main()



        
