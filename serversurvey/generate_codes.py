"""
Takes raw data and generates a set of codes that can be fed into
a neural network training algorithm
"""

import csv, sys

MIN_RESPONSE_COUNT = 50  #The minimum number of times a response code must appear to be considered
MIN_SERVER_COUNT = 50    #The minimum number of times a server type must appear to be considered

def main(argv):

    infile = argv[0]
    outfile = argv[1]

    reader = csv.reader(file(infile, "r"))
    writer = csv.writer(file(outfile, 'w+'), delimiter='\t')
    
    headerIndices = {} #create a dict for easy lookup
    
    #Dictionaries to count responses
    serverCount = {}    #Server type, count
    responseCount = {}  #Response, count
    responses = []  #List of lists
    totalCount = 0

    headerRow = reader.next()
    for i,name in enumerate(headerRow):
        headerIndices[name] = i
    
    for row in reader:

        #Split version string
        serverName = row[ headerIndices['version'] ].split(' ')[0]

        #Ignore empty names - no data here
        if (serverName == "") :
            continue

        #Use a version substring
        versionInfo = serverName.split('/')
        while len(versionInfo) < 2:
            versionInfo.append('')
        serverType = versionInfo[0]
        serverVersion = versionInfo[1]

        requestType = str(row[ headerIndices['requestType']])
           
        #Increment the indices
        serverCount[serverType] = serverCount.get(serverType, 0) + 1

        #Generate the response codes
        responseCodes = [serverType, serverVersion, requestType]
        responseCodes.append(requestType + ':' + str(row[ headerIndices['status']]))
        responseCodes.append(requestType + ':ActualBodyLength:' +str(row[ headerIndices['actualBodyLength']]))
        responseCodes.append(requestType + ':BodyMD5:' +str(row[ headerIndices['bodyMD5']]))
        headers = eval(row[ headerIndices['header']])
        for header in headers.keys() :
            if header != 'Server' :
                for value in headers[header] :
                    responseCodes.append(requestType + ':' + header + ":" + value)
        responses.append(responseCodes)

        for response in responseCodes[3:] :
            responseCount[response] = responseCount.get(response, 0) + 1

    #Decide what to print
    allCodes = []
    for response in responseCount.keys() :
        if responseCount[response] > MIN_RESPONSE_COUNT :
            allCodes.append(response)

    writer.writerow(["Server Type", "Server Version", "Request Type"] + allCodes)

    for responseData in responses :
        serverType = responseData[0]
        serverVersion = responseData[1]
        requestType = responseData[2]
        responseSet = set(responseData[3:])

        if serverCount[serverType] < MIN_SERVER_COUNT :
            continue

        outRow = [serverType, serverVersion, requestType]

        #print outRow
        for code in allCodes :
            if code in responseSet :
                outRow.append(1)
            else :
                outRow.append(0)
        writer.writerow(outRow)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.stderr.write("\nGenerate a data set for a neural network classifier")
        sys.stderr.write("\nSyntax: generate_codes.py [input file] [output file]\n\n")
        sys.exit(1)

    main(sys.argv[1:])
