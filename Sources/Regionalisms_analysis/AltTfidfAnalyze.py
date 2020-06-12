import csv
import math
from UtilityFunctions import getRegionalisms, readRegionalisms

datafolder = "../../data"


def countDocumentOcurences(subreddit_data, word):
    count = 0
    for sub in subreddit_data:
        if float(sub.get(word, -1.0)) > 0:
            count = count + 1
    return count


def calculateIDF(subreddit_data, word, N):
    numdocswithword = countDocumentOcurences(subreddit_data, word)
    if numdocswithword > 0 :
        return math.log(N / float(numdocswithword))
    else:
        print("WARNING, tried to calculate tfidf score of a word without any occurences.")
        return 0


def main(frequencyCSV="results_frequencys.csv"):
    # based off of https://towardsdatascience.com/natural-language-processing-feature-engineering-using-tf-idf-e8b9d00e7e76
    # edited to suit my needs here
    readRegionalisms()
    frequencyCSV_path= datafolder+"/Results/"+frequencyCSV
    regionalisms = getRegionalisms()
    idfscore = dict().fromkeys(regionalisms, 0)
    subreddit_data = list()
    with open(frequencyCSV_path, "r") as frequencyCSV_file:
        csvreader = csv.DictReader(frequencyCSV_file, delimiter=",", dialect='excel')
        for row in csvreader:
            subreddit_data.append(row)
        print(csvreader.fieldnames)

    #should now have a thing of frequencies.
    #calc idf:
    N = len(subreddit_data)
    print("analyzing "+str(N)+" subreddits.")
    for word in regionalisms:
        if word == "Subreddit":
            continue

        idfscore[word] = calculateIDF(subreddit_data, word,  N)


    output = list()
    for i in range(N):
        current_freq = subreddit_data[i]
        print(current_freq.get("Subreddit"))
        tfidf_score_current = dict().fromkeys(regionalisms, 0)
        for word in set(regionalisms).intersection(current_freq.keys()):
            print(str(current_freq.get(word)) + " " + str(idfscore.get(word)))
            tfidf_score_current[word] = float(current_freq.get(word)) * idfscore.get(word) #frequency in doc * idf[word]

        tfidf_score_current["Subreddit"] = current_freq.get("Subreddit")
        output.append(tfidf_score_current)

    #write the data
    datafilepath = datafolder + "/results/results_tfidf.csv"
    open(datafilepath, "x").close()
    csvfile = open(datafilepath, "a+", newline='')
    fieldnames = list()
    fieldnames.append("Subreddit")
    fieldnames.extend(regionalisms)
    csvwriter = csv.DictWriter(csvfile, fieldnames, dialect='excel')
    csvwriter.writeheader()

    for subdata in output:
        print(subdata)
        csvwriter.writerow(subdata)


if __name__ == "__main__":
    main()