import os
from zipfile import ZipFile

from nltk.collocations import *
from nltk.corpus import stopwords
import convokit.util
import json
import re
from os import path

user_pattern = re.compile("/u/")
ufile = "utterances.jsonl"
ufilelen = len(ufile)

stopwords = set(stopwords.words('english'))
regionalisms = set()


###############################################
#### derive file names
###############################################
def getTextFileNames(corpusname, filtered=True):
    outputBasefilename = "../../data/ProcessedData/" + corpusname
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
def addStopWords(extrastopfile=["../../data/supplementalremovedwords.txt"]):
    global stopwords
    readRegionalisms()

    for stopwordfile in extrastopfile:
        extrastopfile = open(extrastopfile, "r")
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

def convertToText(filename, corpusname):
    outputBasefilename = filename[:len(filename)-ufilelen]+corpusname
    with open(filename, "r", errors='ignore', encoding="'utf-8'") as corpus_file:
        for jsonline in corpus_file.readlines():
            current = json.loads(jsonline)
            #normalize
            comment = current["text"]
            comment = comment.lower()
            comment = comment.strip()
            #check if mentions user
            mention = mentionsUser(comment)
            metadata = current["meta"]
            ispost = (None == metadata["top_level_comment"])
            #catagorize
            if(ispost):
                if(mention):
                    #post and mention
                    textfile = open(outputBasefilename+"_pst_mention.txt", "a+", errors='ignore')
                else:
                    #post no mention
                    textfile = open(outputBasefilename+"_pst_nomention.txt", "a+", errors='ignore')
            else:
                if(mention):
                    #not most yes mention
                    textfile = open(outputBasefilename+"_cmt_mention.txt", "a+",  errors='ignore')
                else:
                    #no post no mention
                    textfile = open(outputBasefilename+"_cmt_nomention.txt", "a+",  errors='ignore')
            #save to text file
            textfile.write(comment+" <end_comment>\n")
            textfile.close()
            
    #remove stopwords
    if(path.exists(outputBasefilename+"_cmt_nomention.txt")):
        removestopwords(outputBasefilename+"_cmt_nomention.txt")
    if(path.exists(outputBasefilename+"_cmt_mention.txt")):
        removestopwords(outputBasefilename+"_cmt_mention.txt")
    if(path.exists(outputBasefilename+"_pst_nomention.txt")):
        removestopwords(outputBasefilename+"_pst_nomention.txt")
    if(path.exists(outputBasefilename+"_pst_mention.txt")):
        removestopwords(outputBasefilename+"_pst_mention.txt")

#re-process text files to adjust stopword removal
def removeStopwordsFromConverted(filename, corpusname):
    for file in getTextFileNames(filename, corpusname, filtered=False):
        if(path.exists(file)):
            removestopwords(file)
    return
    


def main():
    addStopWords()
    datadirectory = "../../data"

    toProcess = [("path", "furry"), ("path","furry_irl")]
    #[("subreddit/file/path", "name")]
    processed = [("data/California/LosAngeles.corpus/"+ufile, "LA"),
                 ("data/Pennsylvania/philadelphia.corpus/"+ufile, "philly"),
                 ("data/Georgia/Atlanta.corpus/"+ufile, "atlanta"),
                 ("data/DC/washingtondc.corpus/"+ufile, "DC"),
                 ("data/Florida/Miami.corpus/"+ufile, "Miami"),
                 ("data/Florida/"+"florida.corpus/" + ufile, "Florida"),
                 ("data/Massachusetts/boston.corpus/"+ufile, "Boston"),
                 ("data/Florida/Tallahassee.corpus/" + ufile, "Tallahassee"),
                 ("data/Massachusetts/BostonGaymers.corpus/"+ufile, "Boston_gaymers"),
                 ("data/NewYork/nyc.corpus/"+ufile, "NewYorkCity"),
                 ("data/NewYork/nycgaymers.corpus/"+ufile, "NewYorkCity_gaymers"),
                 ("data/Texas/Dallas.corpus/"+ufile, "Dallas"),
                 ("data/Texas/Houston/houston.corpus/"+ufile, "Houston"),
                 ("data/Texas/Houston/houstontx.corpus/"+ufile, "Houstontx"),
                 ("data/Texas/Houston/houstongamers.corpus/"+ufile, "Houston_gamers"),
                 ("data/Illinois/chicago.corpus/"+ufile, "Chicago"),
                 ("data/Illinois/chicagogamers.corpus/"+ufile, "Chicago_gamers")
                 ]

    toProcess = ["furry_irl", "furry"]
    for corpusname in toProcess:
        print("doing, "+corpusname)
        convokit.util.download("subreddit-"+corpusname, data_dir=datadirectory+"/DataDownloads", use_local=True)

        #create the directory
        if not os.path.exists(datadirectory+"/ProcessedData/"+corpusname):
            os.makedirs(datadirectory+"/ProcessedData/"+corpusname)

        with ZipFile(datadirectory+"/DataDownloads/"+"subreddit-"+corpusname+".corpus.zip") as corpuszip:
            if not os.path.exists(datadirectory+"/ProcessedData/"+corpusname+"/utterances.jsonl"):
                with corpuszip.open() as corpuszipopen:
                    corpuszipopen.extract("utterances.jsonl", path=datadirectory+"/ProcessedData/"+corpusname+"/")

        #convertToText(fileinfo[0], fileinfo[1])
        #removeStopwordsFromConverted(fileinfo[0], fileinfo[1])
        
        
if __name__ == "__main__":
    main()



        
