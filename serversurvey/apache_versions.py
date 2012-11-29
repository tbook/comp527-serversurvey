# apache_versions.py
#
# Counts Apache version strings, among other things.

import csv,sys,argparse
import re
from operator import itemgetter

# globals #
version_regex = re.compile("\d([.]\d)*")

"""
# probabilistic methods #
def train_probabilities(filename):
    '''
    When given the name of a CSV, returns
    '''
    # load training data
    csvfile = file(filename,"r")
    reader = csv.reader(csvfile)

    #Data
    headerIndices = {}  #Index for each field in input files
    versionResponseCounts = {}  #Dict of sets, containing all the responses for each version
    versionCounts = {}   #The number of sites reporting each version type
    responseCounts = {} #The total count of each response
    siteVersions = {}    #Dict giving the version type for each site
    totalCount = 0      #The total number of sites

    # grab the first row and use it as the header
    indices = {}
    header = reader.next()
    for i,name in enumerate(header):
        indices[name] = i

    #
    for row in reader:
        raw_version = row[indices['version']]
        
        #Generate the response code
        responseCode = str(row[ indices['requestType']]) + str(row[ indices['status']])

        siteName = row[headerIndices['requestUrl']]
            
        #Ignoring non-apache and empty versions, store:
        if (is_apache( raw_version ) and not get_version(raw_version) == ""):
            thisVersionResponses = versionResponseCounts.get(versionName, {})
            thisResponseCount = thisVersionResponses.get(responseCode, 0)
            thisResponseCount = thisResponseCount + 1
            thisVersionResponses[responseCode] = thisResponseCount
            versionResponseCounts[versionName] = thisVersionResponses
            
            thisResponseCount = responseCounts.get(responseCode, 0)
            thisResponseCount = thisResponseCount + 1
            responseCounts[responseCode] = thisResponseCount
            
            siteVersions[siteName] = versionName

    #Calculate statistics on the dataset
    for site in siteVersions.keys() :
        totalCount = totalCount + 1
        thisVersion = siteVersions[site]
        thisVersionCount = versionCounts.get(thisVersion, 0)
        thisVersionCount = thisVersionCount + 1
        versionCounts[thisVersion] = thisVersionCount

    # return

def guess_apache_versions(loadfile, training):
    '''
    When given a CSV of server data to load and the training above, assign
    versions to Apache servers with certainty and save the result.
    '''

    # load data
    csvfile = file(loadfile,"r")
    reader = csv.reader(csvfile)
    reader.next()   #Dump the headers
    
    #Build a dict with all of the responses and versions for each site    
    site_response_dict = {}   #Dict of lists of all responses for a given site
    reported_version = {}     #Reported version from a single site
    for row in reader:
        url = row[ headerIndices['requestUrl'] ]
        responce = str(row[ headerIndices['requestType']]) \
            + str(row[ headerIndices['status']])
        siteResponses = site_response_dict.get(url, [])
        siteResponses.append(responce)
        site_response_dict[url] = siteResponses
        
        # Get reported version
        version = get_version( row[ headerIndices['version'] ] )
        reported_version[url] = version
    
    #Predict the version for each site
    finalProbs = {}     #Dict of dicts - each included dict is probability for a given version
    
    for site in site_response_dict.keys() :
        versionFinalProbs = {}
        for server in serverCounts.keys() :
            pProductServer = 1.0
            pProductNotServer = 1.0
            for response in site_response_dict[site] :
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
                versionFinalProbs[server] = pThisServer
        finalProbs[site] = versionFinalProbs
        
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
        writer.writerow([site, reported_version[site], likelyServer, serverProbability])
"""

# counting methods #
def is_apache(server_string):
    '''
    When given a server string like 'Apache-2.2.0', return true if it represents
    an Apache string.
    '''
    apache_strings = ["Apache", "IBM_HTTP_Server"]
    result = False

    for apache_string in apache_strings:
        #if apache_string.lower() in server_string.lower():
        if server_string[ : len(apache_string)] == apache_string:
            result = True
            continue

    return result

def get_version(server_string):
    '''
    When given a server string like 'Apache-2.2.0', returns the version
    string in a reasonable format.

    eg "Coyote/1.1", "2.2.0"
    '''
    version = ""

    split_string = server_string.split("/")

    # if version is properly provided...
    if len(split_string) > 1:

        # we want to keep Coyote in the version string
        if "coyote" in server_string.lower():
            version = "Coyote/"
        elif "ibm_http" in server_string.lower():
            version = "IBM_HTTP_Server/"

        # only keep 2.2.2. ... type strings
        v = version_regex.match(split_string[1])
        if v != None:
            version += version_regex.match(split_string[1]).group()

    return version

def load_version_strings(filename):
    '''
    When given the filename of a CSV where a dict with 'server' in the second to
    last column, return a dictionary of apache versions with counts.
    '''

    # open csv
    csvfile = file(filename, "r")
    reader = csv.reader(csvfile)
    
    reader.next() # trash headers

    # read
    apache_versions = {}

    for row in reader:
        server_dict = eval(row[-2])

        try:
            server_string = str(server_dict['Server'][0])

            if is_apache(server_string):
                version = get_version(server_string)

                if not version in apache_versions.keys():
                    apache_versions[version] = 0
                apache_versions[version] += 1
        except KeyError as e:
            continue

    csvfile.close()
    return apache_versions


def main(argv):

    parser = argparse.ArgumentParser(description="Count apache version strings and write results to output.")
    parser.add_argument("-i", nargs=1, help="input file")
    parser.add_argument("-t", nargs=1, help="training file")
    parser.add_argument("-o", nargs=1, help="output file")
    args = parser.parse_args()

    input = "survey-bottom-10k.csv"
    output = "apache_version_counts.csv"
    if args.i != None: input = args.i[0]
    if args.o != None: output = args.o[0]
    #training = args.t[0]

    # Read in versions
    apache_versions = load_version_strings(input)

    # Write results
    print apache_versions
    sorted_keys = sorted(apache_versions)

    csvwrite = file(output,"w+")
    writer = csv.writer(csvwrite)
    for server in sorted_keys:
        row = []
        row.append(server)
        row.append(apache_versions[server])
        print row
        writer.writerow(row)

    csvwrite.close()

if __name__ == "__main__":
    main(sys.argv[1:])
