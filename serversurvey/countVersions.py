# Counts the number of versions of a server in a csv file
# baysian analysis of a dataset.

import csv, sys, argparse

def main(argv):

    parser = argparse.ArgumentParser(description="Predict server types based on responses to queries")
    parser.add_argument("-i", nargs=1, help="input file")
    parser.add_argument("-o", nargs=1, help="output file")
    args = parser.parse_args()

    #Read the training data
    infile = args.i[0]
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
            
            siteServerList = siteServers.get(siteName, set())
            siteServerList.add(serverName)
            siteServers[siteName] = siteServerList

    #Calculate statistics on the dataset
    for site in siteServers.keys() :
        totalCount = totalCount + 1
        siteServerList = siteServers[site]
        for thisServer in siteServerList :
            thisServerCount = serverCounts.get(thisServer, 0)
            thisServerCount = thisServerCount + 1
            serverCounts[thisServer] = thisServerCount
    #Write the results

    outfile = args.o[0]
    writer = csv.writer(file(outfile, 'w+'), delimiter='\t')
    #Write counts for each server type
    for server in serverCounts.keys() :
        writer.writerow([server, serverCounts[server]]);
    """
    #Write servers for each site
    for site in siteServers.keys() :
        row = [site, len(siteServers[site])]
        for server in siteServers[site] :
            row.append(server)
        writer.writerow(row)
    """


if __name__ == "__main__":
    main(sys.argv[1:])
                
                
