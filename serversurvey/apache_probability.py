# apache_probability.py
#
# Guesses apache versions (optionally just 2.2 or 2 / Coyote / 1 / 0)
import csv,sys,argparse
import re
from apache_versions import is_apache

# global regex #
all_version_regex = re.compile("\d+([.][0-9xX]+)*")
minor_version_regex = re.compile("\d+([.]\d+)?")
major_version_regex = re.compile("\d+") #TODO: not the best way to pick out

number_regex = re.compile("\d")

# regex methods #
def re_get_version(server_string, regex):
    '''
    Return a server version using regex.
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
        v = regex.match(split_string[1])
        if v != None:
            version += v.group()
        
        # add a .X to every version if we're not using the all regex
        if regex != all_version_regex and len(version)>0:
            if number_regex.match(version[-1]) != None:
                version += ".X"
            if version[-1] == ".": # add an X to decimals
                version += "X"

    return version

# probabilistic methods #
def train_probabilities(filename, regex):
    '''
    When given the name of a CSV and the regex used to parse versions, returns
    '''
    # load training data
    csvfile = file(filename,"r")
    reader = csv.reader(csvfile)

    # p(Version), p(Response), p(Response | Version)
    versionResponseCounts = {}  #Dict of sets, containing all the responses for each version

    versionCounts = {}  #Number of sites reporting each version type (pVersion)
    responseCounts = {} #Total number of responses (for pResponse)
    siteVersions = {}   #Dict giving the version type for each site (
    totalCount = 0      #The total number of sites (# points,pVersion pResponse)

    # grab the first row and use it as the header
    indices = {}
    header = reader.next()
    for i,name in enumerate(header):
        indices[name] = i

    #
    for row in reader:
        raw_version = row[indices['version']]
        versionName = re_get_version(raw_version,regex)
        responseCode = str(row[ indices['requestType']]) + str(row[ indices['status']])
        siteName = row[indices['requestUrl']]
            
        #Ignoring non-apache and empty versions, fill our data:
        if (is_apache( raw_version ) and not versionName == ""):
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

    # return dicts for P(version), P(response), and P(response | version)
    # so (versionCounts, responseCounts, versionResponseCounts)
    return (versionCounts, responseCounts, versionResponseCounts, totalCount)

def guess_apache_versions(loadfile,outfile,regex, version_counts, response_counts, version_response_counts, totalCount):
    '''
    When given a CSV of server data to load, the regex to parse versions, and 
    the training above, assign versions to Apache servers with certainty and 
    save the result.
    '''

    # load data
    csvfile = file(loadfile,"r")
    reader = csv.reader(csvfile)
    
    # grab the first row and use it as the header
    indices = {}
    header = reader.next()
    for i,name in enumerate(header):
        indices[name] = i
    #print indices

    #Build a dict with all of the responses and versions for each site    
    site_response_dict = {}   #Dict of lists of all responses for a given site
    reported_version = {}     #Reported version from a single site
    for row in reader:
        url = row[ indices['requestUrl'] ]
        response = str(row[ indices['requestType']]) \
            + str(row[ indices['status']])
        site_responses = site_response_dict.get(url, [])
        site_responses.append(response)
        site_response_dict[url] = site_responses
        
        # Get reported version
        raw_version = row[indices['version']]
        if (is_apache(raw_version)) :
            version = re_get_version(raw_version, regex )
            #print("Interpreted " + row[indices['version']] + " as " + version)
            reported_version[url] = version
    
    #Predict the version for each site
    finalProbs = {}     #Dict of dicts - each included dict is probability for a given version
    
    for site in reported_version.keys() :
        versionFinalProbs = {}
        for version in version_counts.keys() :
            #print version,version_counts[version], version_response_counts[version]
            pProductVersion = 1.0
            pProductNotVersion = 1.0
            for response in site_response_dict[site] :
                pResponseGivenVersion = float(version_response_counts[version].get(response,0)) / version_counts[version]

                #if version_response_counts[version].get(response,0) == 0:
                #    print "hey",version_response_counts[version],version,response

                pProductVersion = pProductVersion * pResponseGivenVersion
                pResponseNotVersion = float(response_counts.get(response,0) - version_response_counts[version].get(response,0)) / (totalCount - version_counts.get(version,0))
                pProductNotVersion = pProductNotVersion * pResponseNotVersion
            pVersion = float(version_counts[version]) / totalCount
            pNotVersion = float(totalCount - version_counts[version]) / totalCount
            denominator = pVersion * pProductVersion + pNotVersion * pProductNotVersion
            if (denominator == 0):
                print "Invalid data for version " + version + " on site " + site ,pVersion,pProductVersion,pNotVersion,pProductNotVersion,pResponseGivenVersion
            else:
                pThisVersion = pVersion * pProductVersion / denominator
                versionFinalProbs[version] = pThisVersion
        finalProbs[site] = versionFinalProbs
        
    #Write the results        
    writer = csv.writer(file(outfile, 'w+'))#, delimiter='\t')
    
    #print a header
    writer.writerow(["Site","Reported Version","Calculated Version","Probability"])
    
    for site in finalProbs.keys():
        likelyVersion = "unknown"
        versionProbability = 0.0
        for version in finalProbs[site].keys():
            if (finalProbs[site][version] > versionProbability):
                likelyVersion = version
                versionProbability = finalProbs[site][version]
        writer.writerow([site, reported_version[site], likelyVersion, versionProbability])

def main(argv):

    # parse command line input
    parser = argparse.ArgumentParser(description="Guess Apache versions and write o output's csv. Tries to guess minor versions by default.")
    parser.add_argument("-i", nargs=1, help="input file")
    parser.add_argument("-t", nargs=1, help="training file")
    parser.add_argument("-o", nargs=1, help="output file")

    parser.add_argument("-regex", nargs=1, help="regex to guess versions. Valid fields: major, minor, exact")
    args = parser.parse_args()

    #Default values
    input = "survey-bottom-10k.csv"
    output = "apache_version_guesses.csv"
    regex = minor_version_regex

    #Values from arguments
    if args.i != None:
        input = args.i[0]
    if args.o != None:
        output = args.o[0]
    training = input
    if args.t != None:
        training = args.t[0]

    if args.regex[0] !=None:
        if args.regex[0] == "minor":
            regex = minor_version_regex
            print "setting regex to minor"
        elif args.regex[0] == "major":
            regex = major_version_regex
            print "setting regex to major"
        elif args.regex[0] == "exact":
            regex = all_version_regex
            print "setting regex to exact"
        else:
            print "invalid option",args.regex[0]+", using minor versions." 

    # analyze
    (versionCounts, responseCounts, versionResponseCounts, totalCount) = train_probabilities(training,regex)
    guess_apache_versions(input, output, regex, versionCounts, responseCounts, versionResponseCounts, totalCount)

        

if __name__ == "__main__":
    main(sys.argv[1:])
