# RegionalismsOnReddit
**Identifying regionalisms and when they're used on Reddit.com**<br>
A repo for my Sociolinguistics and NLP final projects.
<br><br>
There are two main goals of this project. The first goal is to try and detect in what context people use regionalisms the most on Reddit. For this analysis I used Umashanthi Pavalanathan, and Jacob Eisenstein's paper [Audience-Modulated Variation in Online Social Media](https://www.semanticscholar.org/paper/AUDIENCE-MODULATED-VARIATION-IN-ONLINE-SOCIAL-MEDIA-Pavalanathan-Eisenstein/9559f5cb044b1a6320225dd8b754adcbf1b20efe) to augment my inital list of informal regionalisms and for comparason.
<br><br>
The second goal of this project is to automatically detect and identify regionalisms in Reddit comments. To do this, I used TF-IDF scores and known regionalisms to identify a range of values that regionalisms were likely to occur between and extracted all words within that range. 

# Example - Finding out where and how much pitsburgeese is used
1. Replace the contents of data/CurrentSubredditSet.txt with "pittsburgh" which is a big Pittsburgh subreddit
1. Replace the contents of data/regionalisms.txt with the list of regionalisms bellow 
1. Run ProcessToText.py to pre-process the text, this will take a few minutes.
1. Run Analyze.py
1. You should then get a few .csv files in the data/results folder to look at with how often each of those words is used

* results_audience.csv is how often one of the words is used in different contexts. 
* results_frequencys.csv is how frequent each of these words is used.
* results_counts.csv is the number of occurrences 
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
[Natural Language Toolkit (NLTK)](https://www.nltk.org/)<br>
```pip install nltk```


[Convo Kit](https://convokit.cornell.edu/documentation/tutorial.html)<br>
```pip install convokit```


## Downloading/Selecting Data
To download the corpus files, you can download them directly from [this](https://zissou.infosci.cornell.edu/convokit/datasets/subreddit-corpus/corpus-zipped/) alphabetical index. Then move the zipped files into the data/DataDownloads folder. 
<br>

See the following link for more information: <br>
https://convokit.cornell.edu/documentation/subreddit.html

<br>
Alternatively the data will automatically be downloaded when you run the the ProcessToText.py file that pre-processes the data. 
<br>
To choose the subreddits used, edit the data/CurrentSubredditSet.txt file and write the names of subreddits, which are case sensitive, on their own line. All the scripts use this file to choose what to work with.

# Future Work and Spin off Ideas
First of all, this project needs some named entity recognition to strip out proper nouns that fill it up. Currently (6/13/2020), the TF-IDF based filtering works great, especially when you add more subreddits, but the data is largely filled with local politicians, street names, and places. On the one hand, I'm extremely happy it's finding local stuff, including the regionalisms, on the other hand, it's unusable other than as proof that the idea works.<br>
- [ ] Proper Noun removal with named entity recognition
- [ ] Number removal (while still allowing ASCII faces, or words in the regionalisms.txt to remain
- [ ] Better bot detection and removal
- [ ] Better URL removal
- [ ] Make the package more user friendly, and allow for integration with other projects. 
<br><br>
I failed to get to my goal of dynamically identifying that range of tf-idf values which would be important in making this useful, however it might still be fine as long as you have a city with known regionalisms to set the tf-idf score range with. <br><br>
I really wanted to use this project as a spring board for looking at linguistic similarities between internet communities, so, getting some working hierarchical document classification would be really nice.
<br><br>
In a similar vain, mapping terms would be another cool spin off. There are plenty of linguistic maps for how spoken language varies, but not vocabulary. The only part remaining for this would be a way to go from a subreddit's name to a location on a map, and then coloring the map.<br><br>
