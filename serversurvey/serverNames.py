# Calculates the probable server names for each site based on
# baysian analysis of a dataset.

import csv, sys, argparse, urlparse

ZERO_PROB = 0.000001

def makeResponseCodes(row, headerIndices):
    """
    Returns a list with all of the response codes for a given input line
    """
    responseCodes = []
    responseCodes.append(str(row[ headerIndices['requestType']]) + ':' + str(row[ headerIndices['status']]))
    responseCodes.append(str(row[ headerIndices['requestType']]) + ':ActualBodyLength:' +str(row[ headerIndices['actualBodyLength']]))
    responseCodes.append(str(row[ headerIndices['requestType']]) + ':BodyMD5:' +str(row[ headerIndices['bodyMD5']]))
    headers = eval(row[ headerIndices['header']])
    for header in headers.keys() :
        if header != 'Server' :
            for value in headers[header] :
                responseCodes.append(str(row[ headerIndices['requestType']]) + ':' + header + ":" + value)
    return responseCodes

def getServerType(userAgent):
    """
    Converts a user agent string into a standard server type
    """
    #Split version string
    #serverName = userAgent.split(' ')[0]

    versionInfo = userAgent.split('/')
    while len(versionInfo) < 2:
        versionInfo.append('')
    serverName = versionInfo[0]
    serverVersion = versionInfo[1]
    return serverName

def main(argv):

    #Data
    headerIndices = {}  #Index for each field in input files
    serverResponseCounts = {}  #Dict of sets, containing all the responses for each server
    serverCounts = {}   #The number of sites reporting each server type
    responseCounts = {} #The total count of each response
    siteServers = {}    #Dict giving the server type for each site
    totalCount = 0      #The total number of sites

    parser = argparse.ArgumentParser(description="Predict server types based on responses to queries")
    parser.add_argument("-i", nargs=1, help="input file")
    parser.add_argument("-t", nargs=1, help="training file")
    parser.add_argument("-o", nargs=1, help="output file")
    args = parser.parse_args()

    #Read the training data
    infile = args.t[0]
    reader = csv.reader(file(infile, "r"))

    # grab the first row and use it as the header
    headerRow = reader.next()
    for i,name in enumerate(headerRow):
        headerIndices[name] = i    

    for row in reader:
        
        #Get server name and site name
        serverName = getServerType(row[headerIndices['version']])
        siteName = urlparse.urlparse(row[headerIndices['requestUrl']]).hostname
        #Ignore empty names - no data here
        if (serverName == "") :
            continue

        #Generate the response codes
        responseCodes = makeResponseCodes(row, headerIndices)
        
        #Store the results
        for responseCode in responseCodes :
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
    siteResponseDict = {}   #Dict of lists of all responses for a given site
    siteReportedServer = {} #Reported server type for a given site
    for row in reader:
        siteName = urlparse.urlparse(row[ headerIndices['requestUrl'] ]).hostname
        serverName = getServerType(row[headerIndices['version']])

        responseCodes = makeResponseCodes(row, headerIndices)

        siteResponses = siteResponseDict.get(siteName, [])
        for responseCode in responseCodes :
            siteResponses.append(responseCode)
        siteResponseDict[siteName] = siteResponses
        
        siteReportedServer[siteName] = serverName
    
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
                pResponseNotServer = float(responseCounts.get(response,0) \
                    - serverResponseCounts[server].get(response,0)) / \
                    (totalCount - serverCounts.get(server,0))

                if (pResponseNotServer > 0.0) and (pResponseGivenServer > 0.0) :  #Ignore where inadequate data
                    pProductNotServer = pProductNotServer * pResponseNotServer
                    pProductServer = pProductServer * pResponseGivenServer
                print "Server: " + server + " Response: " + response
                print "pResponseGivenServer: " + str(pResponseGivenServer)
                print "pResponseNotServer: " + str(pResponseNotServer)
            pServer = float(serverCounts[server]) / totalCount
            pNotServer = float(totalCount - serverCounts[server]) / totalCount
            #print "pServer: " + str(pServer) + " pProductServer: " + str(pProductServer) + " pNotServer: " + str(pNotServer) + " pProductNotServer: " + str(pProductNotServer)

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
    
    #print a header
    writer.writerow(["Site","Reported Server","Calculated Server","Probability"])
    
    for site in finalProbs.keys():
        likelyServer = "unknown"
        serverProbability = 0.0
        for server in finalProbs[site].keys():
            if (finalProbs[site][server] > serverProbability):
                likelyServer = server
                serverProbability = finalProbs[site][server]
        writer.writerow([site, siteReportedServer[site], likelyServer, serverProbability])

if __name__ == "__main__":
    main(sys.argv[1:])
                
                
