import argparse
import csv
import urlparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Estimate the accuracy of estimation")
    parser.add_argument("-r", nargs=1, help="raw results", required=True)
    parser.add_argument("-c", nargs=1, help="calculated results", required=True)
    parser.add_argument("-t", nargs=1, help="training data", required=True)
    parser.add_argument("-o", nargs=1, help="output file", required=True)
    args = parser.parse_args()

    trainingFile = args.t[0]
    trainingReader = csv.reader(file(trainingFile, "r"), delimiter='\t')
    trainingHeader = trainingReader.next()

    rawFile = args.r[0]
    rawReader = csv.reader(file(rawFile, "r"))
    rawHeader = rawReader.next()
    rawIndices = {}
    for i,name in enumerate(rawHeader):
        rawIndices[name] = i

    estFile = args.c[0]
    estReader = csv.reader(file(estFile, "r"))
    estHeader = estReader.next()

    outputFile = args.o[0]
    outputWriter = csv.writer(file(outputFile, "w"))
    outputWriter.writerow(['site', 'depth', 'estimate', 'actual...'])

    #See which server types we are estimating
    includedTypes = set()
    for row in trainingReader :
        serverType = row[0]
        includedTypes.add(serverType)

    #Read the actual values
    sites = {}  #Dict of sitename, set(servertypes)
    for row in rawReader :
        url = row[rawIndices['requestUrl']]
        site = urlparse.urlparse(url).hostname
        realTypes = sites.get(site, set())
        realType = row[rawIndices['version']]
        if (realType in includedTypes) :
            realTypes.add(row[rawIndices['version']])
            sites[site] = realTypes

    noCorrect = [0,0,0,0]
    noWrong = [0,0,0,0]
    noIgnored = [0,0,0,0]

    for row in estReader :
        for position, function in enumerate([ \
            lambda x: x.split('/')[0], \
            lambda x: (x.split('/')[0] + '/' + x.split('/')[1]).split('.')[0], \
            lambda x: x.split('.')[0] + '.' + x.split('.')[1], \
            lambda x: '.'.join(x.split('.')[0:2]) + '.' + x.split('.')[2]    ]) :
            try :
                site = row[0]
                estType = function(row[1])
                realTypes = [function(x) for x in sites.get(site, set())]
                if site in sites.keys() :
                    realTypes = [function(x) for x in sites[site]]
                    if estType in realTypes :
                        noCorrect[position] += 1
                    else :
                        noWrong[position] += 1
                    outputWriter.writerow([site, position, estType] + list(realTypes))
                else :
                    noIgnored[position] += 1
                #print "Comparing: " + estType + ", " + ", ".join(realTypes)
            except IndexError :
                #print "Error at level " + str(position) + " for " + row[1] + ", " + ', '.join(list(sites.get(site,set())))
                while position < 4 :
                    noIgnored[position] += 1
                    position += 1
                break

    print "Correct: " + str(noCorrect)
    print "Incorrect: " + str(noWrong)
    print "Ignored: " + str(noIgnored)

