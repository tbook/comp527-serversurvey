"""
Counts the number of instances of a given server type for a given code
"""

import csv, sys

MIN_RESPONSE_COUNT = 1000  #The minimum number of times a response code must appear to be considered
MIN_SERVER_COUNT = 500  #The minimum number of times a server type must appear to be considered

def main(argv):

    infile = argv[0]
    outfile = argv[1]

    reader = csv.reader(file(infile, "r"))
    writer = csv.writer(file(outfile, 'w+'), delimiter='\t')
    
    headerIndices = {} #create a dict for easy lookup
    
    #Dictionaries to count responses
    serverCount = {}            #Servertype, number of occurances
    serverResponseCount = {}    #Dict of dicts
    responseCount = {}          #ResponseCode, number of occurances
    totalCount = 0              #Total number of response codes (excluding ignored)

    headerRow = reader.next()
    for i,name in enumerate(headerRow):
        headerIndices[name] = i
    
    for row in reader:

        #Split version string
        serverName = row[ headerIndices['version'] ].split(' ')[0]

        #Ignore empty names - no data here
        if (serverName == "") :
            continue
        if (serverName == "-") :
            continue

        #Use a version substring
        versionInfo = serverName.split('/')
        while len(versionInfo) < 2:
            versionInfo.append('')
        serverType = versionInfo[0]
        serverVersion = versionInfo[1]
                    
        #Increment the indices
        serverCount[serverName] = serverCount.get(serverName, 0) + 1
        
        if (serverResponseCount.has_key(serverName)):
            thisServerResponseCount = serverResponseCount[serverName]
        else:
            thisServerResponseCount = {}

        #Generate the response codes
        responseCodes = []
        responseCodes.append(str(row[ headerIndices['requestType']]) + ':' + str(row[ headerIndices['status']]))
        responseCodes.append(str(row[ headerIndices['requestType']]) + ':ActualBodyLength:' +str(row[ headerIndices['actualBodyLength']]))
        responseCodes.append(str(row[ headerIndices['requestType']]) + ':BodyMD5:' +str(row[ headerIndices['bodyMD5']]))
        headers = eval(row[ headerIndices['header']])
        for header in headers.keys() :
            if header != 'Server' :
                for value in headers[header] :
                    responseCodes.append(str(row[ headerIndices['requestType']]) + ':' + header + ":" + value)

        for responseCode in responseCodes :
            thisServerResponseCount[responseCode] = thisServerResponseCount.get(responseCode, 0) + 1
            responseCount[responseCode] = responseCount.get(responseCode, 0) + 1

        serverResponseCount[serverName] = thisServerResponseCount
                        
    #Decide which codes to include
    responseCodes = []
    for code in responseCount.keys():
        if (responseCount[code] >= MIN_RESPONSE_COUNT) :
            responseCodes.append(code)
            totalCount = totalCount + responseCount[code]

    #Remove data for ignored servers
    for server in serverCount.keys():
        thisServerResponseCount = serverResponseCount[server]
        if (serverCount[server] < MIN_SERVER_COUNT) :    
            for code in responseCodes :
                responseCount[code] -= thisServerResponseCount.get(code, 0)
                totalCount -= thisServerResponseCount.get(code, 0)
            del serverCount[server]

    #Print a table of all results

    #Write the output headers
    writer.writerow(['Server', 'Server Count'] + responseCodes)
    
    #Write the output for each server
    for server in serverCount.keys():
        thisServerResponseCount = serverResponseCount[server]
        outRow = []
        outRow.append(server)
        outRow.append(serverCount[server])
        for code in responseCodes:
            outRow.append(thisServerResponseCount.get(code,0))
        writer.writerow(outRow);
    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.stderr.write("\nCounts the number of times a code appears for a given server type")
        sys.stderr.write("\nSyntax: count.py [input file] [output file]\n\n")
        sys.exit(1)

    main(sys.argv[1:])
