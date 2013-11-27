"""
Script to infer the correct type for a server based on a pre-compiled database of probabilities
"""

import argparse
import csv
import urlparse
import math

LAPLACE_CONSTANT = 1 #For Laplace smoothing

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict server types based on a training file")
    parser.add_argument("-i", nargs=1, help="input file", required=True)
    parser.add_argument("-t", nargs=1, help="training file", required=True)
    parser.add_argument("-o", nargs=1, help="output file", required=True)
    args = parser.parse_args()

    #Open the output file
    outputFile = args.o[0]
    outputWriter = csv.writer(file(outputFile, "w"))
    outputWriter.writerow(["Site", "Server Type", "Probability"])

    #Read the training data
    serverCounts = {}   # Count for each server type in training data
    responseCounts = {}  # Count for a given response code across all server types
    servers = {}    #Dict of {response, count}
    totalServerCount = 0

    trainingFile = args.t[0]
    trainingReader = csv.reader(file(trainingFile, "r"), delimiter='\t')
    trainingHeader = trainingReader.next()

    for row in trainingReader :
        serverType = row[0]
        serverCounts[serverType] = int(row[1])
        totalServerCount += int(row[1])

        counts = {}
        for index, code in enumerate(trainingHeader[2:]) :
            index = index + 2
            counts[code] = int(row[index])
            responseCounts[code] = responseCounts.get(code, 0) + int(row[index])
        servers[serverType] = counts

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
        siteResponses = siteData[site]

        mostProbable = None
        highestProbability = float('-inf')

        for serverType in servers.keys() :

            counts = servers[serverType] 
            pServer = float(serverCounts[serverType]) / float(totalServerCount)
            logCodeServer = math.log(pServer, 2)
            logNotCodeServer = math.log(1 - pServer, 2)

            for code in counts.keys() :
                pCodeServer = float(counts[code] + LAPLACE_CONSTANT) \
                    / float(serverCounts[serverType] + LAPLACE_CONSTANT)
                pNotCodeServer = float((serverCounts[serverType] - counts[code]) + LAPLACE_CONSTANT) \
                    / float(serverCounts[serverType] + LAPLACE_CONSTANT)

                if code in siteResponses :  #Add P(code | server)
                    logCodeServer += math.log(pCodeServer, 2)
                    logNotCodeServer += math.log(pNotCodeServer, 2)
                else:   #Add P(!code | server)
                    logCodeServer += math.log(pNotCodeServer, 2)
                    logNotCodeServer += math.log(pCodeServer, 2)

            #Calculate the probability for this server type
            pThisServer = logCodeServer

            if pThisServer >= highestProbability :
                mostProbable = serverType
                highestProbability = pThisServer

        outLine = [site, mostProbable, highestProbability]
        
        outputWriter.writerow(outLine)



