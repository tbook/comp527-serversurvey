"""
analyze.py

Analyze the survey_data.csv we retrieve with the crawler.
"""

import csv

def f(serverVersion, requestID, status):
    """
    When given the server version string, request ID, and HTTP status, associate the status returned for a given request ID with the server versions.
    """
    print 'not implemented'


if __name__ == "__main__":

    # open survey_data.csv and read it
    csvFile = open('survey_data.csv', 'rb')
    reader = csv.reader( csvFile )

    # TODO: grab this header from the CSV file in the future please
    headerRow = ['requestUrl',
                 'responseUrl', 
                 'status',
                 'requestType',
                 'requestMethod',
                 'version',
                 'contentType',
                 'contentLength',
                 'actualBodyLength',
                 'header'
                 ]
    h = {} # bwahahahaha... create a dict for easy lookup
    for i,name in enumerate(headerRow):
        h[name] = i


    # back to reading

    servers = {}

    n=0
    for row in reader:

        # grab the first row and use it as the header
        if n == 0:
            n += 1
            headerRow = row

        # otherwise, do whatever
        rawVersion = row[ h['version'] ]
        requestID = row[ h['requestType'] ]
        status = row[ h['status'] ]

        print h['version'] == 5, row[ h['version'] ]

        # get versions
        versionInfo = rawVersion.split('/')
        while len(versionInfo) < 2:
            versionInfo.append('')

        serverName = versionInfo[0]
        serverVersion = versionInfo[1]

        # if there is no given server version or name, stick in NONE
        if serverName == '':
            serverVersion = 'NONE'
        if serverVersion == '':
            serverVersion = 'NONE'

        # check to see if there is a version dict already
        if not serverName in servers.keys():
            servers[serverName] = {}

        # check to see if there is a server dict already
        if not serverVersion in servers[serverName].keys():
            servers[serverName][serverVersion] = {}

        # check to see if we have a dict for requestID already
        if not requestID in servers[serverName][serverVersion].keys():
            servers[serverName][serverVersion][requestID] = {}

        # check to see if we're already counting the status there already
        if not status in servers[serverName][serverVersion][requestID].keys():
            servers[serverName][serverVersion][requestID][status] = 1

        # now we can finally add another to status, I guess
        servers[serverName][serverVersion][requestID][status] += 1

        # arrgh this isn't my typical level of design, really! #

    # woohoo done reading, do things with our data

    # first thing: see if the status for the same versions are the same
    '''

    for sName in servers.keys():
        for sVersion in servers[sName].keys():
            for ID in servers[sName][sVersion]:
                print sName,sVersion,ID,servers[sName][sVersion][ID]
                '''
