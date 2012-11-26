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
    
    #Data
    headerIndices = {}  #Index for each field in input files
    serverResponseCounts = {}  #Dict of sets, containing all the responses for each server
    serverCounts = {}   #The number of sites reporting each server type
    responseCounts = {} #The total count of each response
    siteServers = {}    #Dict giving the server type for each site
    totalCount = 0      #The total number of sites
    
    header = True
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

            siteName = row[headerIndices['requestUrl']]
            
            #Store the results
            thisServerResponses = serverResponseCounts.get(serverName, {})
            thisResponseCount = thisServerResponses.get(responseCode, 0)
            thisResponseCount = thisResponseCount + 1
            thisServerResponses[responseCode] = thisResponseCount
            serverResponseCounts[serverName] = thisServerResponses
            
            thisResponseCount = responseCounts.get(responseCode, 0)
            thisResponseCount = thisResponseCount + 1
            responseCounts[responseCode] = thisResponseCount
            
            siteServers[siteName] = serverName
    
    #Calculate statistics on the dataset
    for site in siteServers.keys() :
        totalCount = totalCount + 1
        thisServer = siteServers[site]
        thisServerCount = serverCounts.get(thisServer, 0)
        thisServerCount = thisServerCount + 1
        serverCounts[thisServer] = thisServerCount
        
    #Interpret the sample data        
    #Read the sample data
    infile = args.i[0]
    reader = csv.reader(file(infile, "r"))
    reader.next()   #Dump the headers
    
    #Build a dict with all of the responses for each site    
    siteResponseDict = {}
    for row in reader:
        siteName = row[ headerIndices['requestUrl'] ]
        responseCode = str(row[ headerIndices['requestType']]) \
            + str(row[ headerIndices['status']])
        siteResponses = siteResponseDict.get(siteName, [])
        siteResponses.append(responseCode)
        siteResponseDict[siteName] = siteResponses
    
    #Predict the server for each site
    finalProbs = {}     #Dict of dicts - each included dict is probability for a given server type
    
    for site in siteResponseDict.keys() :
        serverFinalProbs = {}
        for server in serverCounts.keys() :
            pProductServer = 1.0
            pProductNotServer = 1.0
            for response in siteResponseDict[site] :
                pResponseGivenServer = float(serverResponseCounts[server].get(response,0)) /\
                        serverCounts[server]
                pProductServer = pProductServer * pResponseGivenServer
                pResponseNotServer = float(responseCounts[response] - serverResponseCounts[server].get(response,0)) / (totalCount - serverCounts[server])
                pProductNotServer = pProductNotServer * pResponseNotServer
            pServer = float(serverCounts[server]) / totalCount
            pNotServer = float(totalCount - serverCounts[server]) / totalCount
            denominator = pServer * pProductServer + pNotServer * pProductNotServer
            if (denominator == 0):
                print("Invalid data for server " + server + " on site " + site)
            else:
                pThisServer = pServer * pProductServer / denominator
                serverFinalProbs[server] = pThisServer
        finalProbs[site] = serverFinalProbs
        
    #Write the results        
    outfile = args.o[0]
    writer = csv.writer(file(outfile, 'w+'), delimiter='\t')
    
    for site in finalProbs.keys():
        likelyServer = "unknown"
        serverProbability = 0.0
        for server in finalProbs[site].keys():
            if (finalProbs[site][server] > serverProbability):
                likelyServer = server
                serverProbability = finalProbs[site][server]
        writer.writerow([site, likelyServer, serverProbability])

if __name__ == "__main__":
    main(sys.argv[1:])
                
                
