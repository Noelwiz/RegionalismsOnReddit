import nltk
from nltk.collocations import *
from nltk.corpus import stopwords
import convokit
from convokit import Corpus, download, FightingWords
import json
import re
import string
import os
from os import path

user_pattern = re.compile("/u/")
ufile = "utterances.jsonl"
ufilelen = len(ufile)

stopwords = set(stopwords.words('english'))
regionalisms = set()


###############################################
#### derive file names
###############################################

def getUnfilteredTextFilename(corpusfile, corpusname):
    outputBasefilename = corpusfile[:len(corpusfile)-ufilelen]+corpusname
    return [outputBasefilename+"_cmt_nomention.txt",
            outputBasefilename+"_cmt_mention.txt",
            outputBasefilename+"_pst_nomention.txt",
            outputBasefilename+"_pst_mention.txt"]

def getFilteredTextFilename(corpusfile, corpusname):
    filteredfilename = list()
    for c_filename in getUnfilteredTextFilename(corpusfile, corpusname):
        nameinsert_index = c_filename.rfind("/")
        filteredfilename.append(c_filename[:nameinsert_index+1] + "filtered_" + c_filename[nameinsert_index+1:])
    return filteredfilename


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
def addStopWords():
    global stopwords
    readRegionalisms()
    
    extrastopfile = "data/supplementalremovedwords.txt"
    extrastopfile = open(extrastopfile, "r")
    extrastopfile_text = extrastopfile.read()
    extrastopfile.close()

    #filter out regionalims from the stop words
    stopwords.union(set(extrastopfile_text.split()))
    local_copy = regionalisms.copy()

    #avoid filtering out part of a regionalism if it's two words
    for word in local_copy:
        local_copy.union(set(word.split()))
        
    stopwords.difference_update(regionalisms)


def readRegionalisms():
    regionalisms_file = open("data/regionalisms.txt","r+")
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
    for file in getUnprocessedTextFilename(filename, corpusname):
        if(path.exists(file)):
            removestopwords(file)
    return
    


def main():
    addStopWords()


    processed = [ ]
    #[("subreddit/file/path", "name")]
    toProcess = [("data/California/LosAngeles.corpus/"+ufile, "LA"),
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
    for fileinfo in toProcess:
        print("doing, "+fileinfo[1])
        #convertToText(fileinfo[0], fileinfo[1])
        #removeStopwordsFromConverted(fileinfo[0], fileinfo[1])
        
        
if __name__ == "__main__":
    main()



        
