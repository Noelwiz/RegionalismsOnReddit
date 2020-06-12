import DataProcessing
import Regionalisms_analysis

#this file will run everything that I did for my NLP report.
#except it won't run the analyze wordcount on 3 different sets of subreddits.
#that will have to be done yourself
def main():
    DataProcessing.ProcessToText()
    DataProcessing.ProessToWordcounts()
    Regionalisms_analysis.TfidfAnalyzeWordCountFiles()


if __name__ == "__main__":
    main()
