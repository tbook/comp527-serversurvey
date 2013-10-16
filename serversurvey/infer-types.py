"""
Script to infer the correct type for a server based on a pre-compiled database of probabilities
"""

import argparse
import csv
import urlparse

#Location of fields within input file
CODE = 0
SERVER = 1
PROB = 2
SERVER_COUNT = 3
CODE_COUNT = 4

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict server types based on a training file")
    parser.add_argument("-i", nargs=1, help="input file")
    parser.add_argument("-t", nargs=1, help="training file")
    parser.add_argument("-o", nargs=1, help="output file")
    args = parser.parse_args()

    #Open the output
    outputFile = args.o[0]
    outputWriter = csv.writer(file(outputFile, "w"))
    outputWriter.writerow(["Site", "Predeicted Server", "Probability"])

    #Read the training data
    probabilities = {}  # Server type, set of indicators
    allCodes = set()    # All codes used
    serverCounts = {}   # Count for each server type in training data
    totalServerCount = 0 #Total count for all server types

    trainingFile = args.t[0]
    trainingReader = csv.reader(file(trainingFile, "r"), delimiter='\t')
    trainingHeader = trainingReader.next()

    for row in trainingReader :
        serverType = row[SERVER]

        serverProbs = probabilities.get(serverType, {})
        serverProbs[row[CODE]] = float(row[PROB])
        probabilities[serverType] = serverProbs

        allCodes.add(row[CODE])
        serverCounts[serverType] = int(row[SERVER_COUNT])

    for server in serverCounts.keys() :
        totalServerCount += serverCounts[server]

    print "Identified " + str(len(serverCounts)) + " server types.  " + str(totalServerCount) + " unique servers."

    #Read the input file
    print "Reading site data..."
    siteData = {}   #Maps site name to set of responses

    inputFile = file(args.i[0], "r")
    inputReader = csv.reader(inputFile)
    inputHeader = inputReader.next()
    inputIndices = {}
    for index, name in enumerate(inputHeader) :
        inputIndices[name] = index 

    for row in inputReader :
        site = urlparse.urlparse(row[0]).hostname
        siteResponses = siteData.get(site,set())
        siteResponses.add(str(row[ inputIndices['requestType']]) + ':' + str(row[ inputIndices['status']]))
        siteResponses.add(str(row[ inputIndices['requestType']]) + ':ActualBodyLength:' +str(row[ inputIndices['actualBodyLength']]))
        siteResponses.add(str(row[ inputIndices['requestType']]) + ':BodyMD5:' +str(row[ inputIndices['bodyMD5']]))
        headers = eval(row[ inputIndices['header']])
        for header in headers.keys() :
            if header != 'Server' :
                for value in headers[header] :
                    siteResponses.add(str(row[ inputIndices['requestType']]) + ':' + header + ":" + value)
        siteData[site] = siteResponses

    #Calculate the probabilities for each site
    print "Calculating probabilities..."
    noPredictionCount = 0
    for site in siteData.keys() :
        serverFinalProbs = {}   #Server type, probability
        for serverType in probabilities.keys() :
            serverProbs = probabilities[serverType]
            pServer = float(serverCounts[serverType]) / float(totalServerCount)
            pNotServer = 1 - pServer

            #print "serverCounts[serverType]: " + str(serverCounts[serverType])
            #print "Initial pServer: " + str(pServer)

            for code in siteData[site] :
                if code in allCodes :
                    #print code + " Prob: " + str(serverProbs[code])
                    pServer *= serverProbs.get(code, 0.0)
                    pNotServer *= 1.0 - serverProbs.get(code, 0.0)
                    if pServer == 0.0 :
                        #print "No value for " + code + " on " + serverType
                        break

            denominator = pServer + pNotServer
            if (denominator == 0):
                print("Invalid data for server " + serverType + " on site " + site)
            else:
                pThisServer = pServer / denominator
                serverFinalProbs[serverType] = pThisServer

        v = list(serverFinalProbs.values())
        k = list(serverFinalProbs.keys())
        mostLikely = k[v.index(max(v))]
        if (serverFinalProbs[mostLikely] == 0.0) :
            noPredictionCount += 1
            #print "No prediction for " + site
        else :
            outLine = [site, mostLikely, serverFinalProbs[mostLikely]]
            outputWriter.writerow(outLine)

    print "No prediction for " + str(noPredictionCount) + " servers."


