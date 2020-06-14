# RegionalismsOnReddit
**Identifying regionalisms and when they're used on Reddit.com**
A repo for my Sociolinguistics and NLP final projects.

There are two main goals of this project. The first goal is to try and detect in what context people use regionalisms the most on reddit. For this analysis I used Umashanthi Pavalanathan, and Jacob Eisenstein's paper [Audience-Modulated Variation in Online Social Media]https://www.semanticscholar.org/paper/AUDIENCE-MODULATED-VARIATION-IN-ONLINE-SOCIAL-MEDIA-Pavalanathan-Eisenstein/9559f5cb044b1a6320225dd8b754adcbf1b20efe) to augment my inital list of informal regionalisms and for comparason.

The second goal of this project is to automatically detect and identify regionalisms in reddit comments. To do this, I used TF-IDF scores and known regionalisms to identify a range of values that regionalisms were likely to occur between and extracted all words within that range. 

# Example - Finding out where and how much pitsburgeese is used
1. Replace the contents of data/CurrentSubredditSet.txt with "pittsburgh" which is a big Pittsburgh subreddit
1. Replace the contents of data/regionalisms.txt with the list of regionalisms bellow 
1. Run ProcessToText.py to preprocess the text, this will take a few minutes.
1. Run Analyze.py
1. You should then get a few .csv files in the data/results folder to look at with how often each of those words is used

* results_audience.csv is how often one of the words is used in different contexts. 
* results_frequencys.csv is how frequent each of these words is used.
* results_counts.csv is the number of occurences 
* results_stats.csv is metadata, like how many words were in the data.
## List of Regionalisms for the Example
```
n’at
slippy
crik
jagoff
nebby
buggy
sweeper
sweepers
yinz
yinzers
gumband
dippy
aht
```
courtesy of https://www.pghcitypaper.com/pittsburgh/pittsburghese-dictionary-how-to-translate-the-yinzer-vocabulary/Content?oid=14838287


# Setup:
## Dependencys:
Natural Language Toolkit (NLTK)
```pip install nltk```
https://www.nltk.org/

Convo Kit
```pip install convokit```
https://convokit.cornell.edu/documentation/tutorial.html

## Downloading/Selecting Data
To download the corpus files, you can download them directly from [this](https://zissou.infosci.cornell.edu/convokit/datasets/subreddit-corpus/corpus-zipped/) alphabetical index. Then move the zipped files into the data/DataDownloads folder. 


See the following link for more information:
https://convokit.cornell.edu/documentation/subreddit.html


Alternatively the data will automatically be downloaded when you run the the ProcessToText.py file that pre-processes the data. 

To choose the subreddits used, edit the data/CurrentSubredditSet.txt file and write the names of subreddits, which are case sensitive, on their own line. All the scripts use this file to choose what to work with.
