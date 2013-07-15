"""
Script to infer the correct type for a server based on a pre-compiled database of probabilities
"""

import argparse

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

    #Read the training data
    probabilities = {}  # Server type, set of indicators

    trainingFile = args.t[0]
    trainingReader = csv.reader(file(trainingFile, "r"))
    trainingHeader = trainingReader.next()

    for row in trainingReader :
        serverType = row[SERVER]
        serverProbs = probabilities.get(serverType, set())
        serverProbs.add(row)
        probabilities[serverType] = serverProbs

    #Read the input file
    siteData = {}   #Maps site name to set of responses

    inputFile = args.t[0]
    inputReader = csv.reader(file(inputFile, "r"))
    inputHeader = trainingReader.next()

    for row in inputReader :
        site = row[0]
        siteResponses = siteData.get(site,set())
        siteResponses.add(row)
        siteData[site] = siteResponses

    #Calculate the probabilities for each site
    for site in siteData.keys() :
        serverFinalProbs = {}   #Server type, probability
        for serverType in probabilities.keys() :
            pProductServer = 1.0
            pProductNotServer = 1.0
            for code in serverType :
                pResponseGivenServer = float(serverResponseCounts[server].get(response,0)) /\
                serverCounts[server]
                pProductServer = pProductServer * pResponseGivenServer
                pResponseNotServer = float(responseCounts.get(response,0) - serverResponseCounts[server].get(response,0)) / (totalCount - serverCounts.get(server,0))
                pProductNotServer = pProductNotServer * pResponseNotServer
            pServer = float(serverCounts[server]) / totalCount
            pNotServer = float(totalCount - serverCounts[server]) / totalCount
            denominator = pServer * pProductServer + pNotServer * pProductNotServer
            if (denominator == 0):
                print("Invalid data for server " + server + " on site " + site)
            else:
                pThisServer = pServer * pProductServer / denominator
                serverFinalProbs[server] = pThisServer
        v = list(serverFinalProbs.values())
        k = list(serverFinalProbs.keys())
        mostLikely = k[v.index(max(v))]
        outLine = [site, mostLikely, serverFinalProbs[mostLikely]]
        outputWriter.writeRow(outLine)


