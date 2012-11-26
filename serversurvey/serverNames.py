# Calculates the probable server names for each site based on
# baysian analysis of a dataset.

import csv, sys, argparse

def main(argv):

    parser = argparse.ArgumentParser(description="Predict server types based on responses to queries")
    parser.add_argument("-i", nargs=1, help="input file")
    parser.add_argument("-t", nargs=1, help="training file")
    parser.add_argument("-o", nargs=1, help="output file")
    args = parser.parse_args()

    #Read the training data
    infile = args.t[0]
    reader = csv.reader(file(infile, "r"))
    
    header = True
    headerIndices = {} #create a dict for easy lookup
    
    #Dictionaries to count responses
    serverCount = {}
    serverResponseCount = {}    #Dict of dicts
    responseCount = {}
    totalCount = 0
    
    for row in reader:

        # grab the first row and use it as the header
        if header:
            header = False
            headerRow = row
            for i,name in enumerate(headerRow):
                headerIndices[name] = i
        else:
            #Split version string
            rawVersion = row[ headerIndices['version'] ]
            versionInfo = rawVersion.split('/')
            while len(versionInfo) < 2:
                versionInfo.append('')
            serverName = versionInfo[0]
            serverVersion = versionInfo[1]
            
            #Generate the response code
            responseCode = str(row[ headerIndices['requestType']]) + str(row[ headerIndices['status']])
            
            #Increment the indices
            serverCount[serverName] = serverCount.get(serverName, 0) + 1
            
            if (serverResponseCount.has_key(serverName)):
                thisServerResponseCount = serverResponseCount[serverName]
            else:
                thisServerResponseCount = {}
            thisServerResponseCount[responseCode] = thisServerResponseCount.get(responseCode, 0) + 1
            serverResponseCount[serverName] = thisServerResponseCount
            
            responseCount[responseCode] = responseCount.get(responseCode, 0) + 1
            
            totalCount = totalCount + 1
            
    #Calculate the probabilities for each server
    pServerByCode = {}    #Dict of dicts to hold baysean probabilities
    
    for server in serverCount.keys():
        thisServerResponseCount = serverResponseCount[server]
        probs = {}
        for code in responseCount.keys():
            #Calculate probabilities
            pCodeServer = float(thisServerResponseCount.get(code,0)) / float(serverCount[server])
            pServer = float(serverCount[server]) / float(totalCount)
            pCode = float(responseCount[code]) / float(totalCount)
            pServerCode = pCodeServer * pServer / pCode
            probs[code] = pServerCode
        pServerByCode[server] = probs;
    
    #Interpret the sample data        
    #Read the sample data
    infile = args.i[0]
    reader = csv.reader(file(infile, "r"))
    reader.next()   #Dump the headers

    #Build a dict with the probability of each server type
    serverProbs = {}
    for server in serverCount.keys():
        serverProbs[server] = float(serverCount[server]) / float(totalCount)

    #Build a dict with all of the responses for each site    
    siteResponseDict = {}
    for row in reader:
        siteName = row[ headerIndices['requestUrl'] ]
        responseCode = str(row[ headerIndices['requestType']]) + str(row[ headerIndices['status']])
        siteResponses = siteResponseDict.get(siteName, [])
        siteResponses.append(responseCode)
        siteResponseDict[siteName] = siteResponses
    
    #Predict the server for each site
    finalProbs = {}     #Dict of dicts - each included dict is probability for a given server type
    
    #Calculate the probability for each server type
    for site in siteResponseDict.keys():
        serverFinalProbs = {}
        for server in serverCount.keys():
            probProductServer = 1.0
            probProductNotServer = 1.0
            for response in siteResponseDict[site]:
                probServer = pServerByCode[server][response]
                probProductServer = probProductServer * probServer
                probProductNotServer = probProductNotServer * (1 - probServer)
            denominator = (serverProbs[server] * probProductServer + \
            (1 - serverProbs[server]) * probProductNotServer)
            
            if (denominator == 0):
                print("Invalid data for server " + server + " on site " + site)
            else:
                serverProb = serverProbs[server] * probProductServer / denominator            
                serverFinalProbs[server] = serverProb
        finalProbs[site] = serverFinalProbs
            
    #Write the results        
    outfile = args.o[0]
    writer = csv.writer(file(outfile, 'w+'), delimiter='\t')
    
    for site in finalProbs.keys():
        likelyServer = "unknown"
        serverProbability = 0.0
        for server in finalProbs[site].keys():
            if (siteProbs[server] > serverProbability):
                likelyServer = server
                serverProbability = siteProbs[server]
            writer.writeRow([site, likelyServer, serverProbability])
            print(site)

if __name__ == "__main__":
    main(sys.argv[1:])
