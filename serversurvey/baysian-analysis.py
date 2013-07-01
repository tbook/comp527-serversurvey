"""
Writes the probability of a given server type given a specific response code
"""

import csv, sys

def main(argv):
    infile = argv[0]
    outfile = argv[1]

    reader = csv.reader(file(infile, "r"))
    writer = csv.writer(file(outfile, 'w+'), delimiter='\t')
    
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
            
    #Write the output header
    outRow = []
    outRow.append('server')
    outRow.append('serverCount')
    for code in responseCount.keys():
        outRow.append(code)
    writer.writerow(outRow)
    
    #Write the frequency of each response
    outRow = []
    outRow.append('responseCount')
    outRow.append('')
    for code in responseCount.keys():
        outRow.append(responseCount[code])
    writer.writerow(outRow)    
    
    #Write the output for each server
    for server in serverCount.keys():
        thisServerResponseCount = serverResponseCount[server]
        outRow = []
        outRow.append(server)
        outRow.append(serverCount[server])
        for code in responseCount.keys():
            #Calculate probabilities
            pCodeServer = float(thisServerResponseCount.get(code,0)) / float(serverCount[server])
            pServer = float(serverCount[server]) / float(totalCount)
            pCode = float(responseCount[code]) / float(totalCount)
            pServerCode = pCodeServer * pServer / pCode
            outRow.append(pServerCode)
        writer.writerow(outRow);
        

if __name__ == "__main__":
    main(sys.argv[1:])
