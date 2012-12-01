# apache_versions.py
#
# Counts Apache version strings.

import csv,sys,argparse
import re
from operator import itemgetter

# globals #
version_regex = re.compile("\d+([.][0-9xX]+)*")
standard_version_regex = re.compile("\d([.](\d|X)+)?([.](\d|X)+)?")
#two_digit_regex = re.compile("(\d[.](\d)+)[1]")
three_digit_regex = re.compile("(\d)+[.](\d|Xx)+([.](\d|Xx)+)+")

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
        #if "coyote" in server_string.lower():
        #    version = "Coyote/"
        #elif "ibm_http" in server_string.lower():
        #    version = "IBM_HTTP_Server/"
        if "apache " in split_string[0].lower():
            version = "Apache/"
        elif "apache-advanced" in split_string[0].lower():
            version = "Apache/"
        elif "formilux" in split_string[0].lower():
            version = "Apache/"
            split_string[1] = ""
        elif "coyote-node" in split_string[0].lower():
            version = "Coyote/"
        else:
            version = split_string[0] + "/"

        # only keep 2.2.2. ... type strings
        v = version_regex.match(split_string[1])
        if v != None:
            version += version_regex.match(split_string[1]).group()

            # tweaks
            if version == "Apache/2.00":
                version = "Apache/2.0.X"
            if version == "Apache/2.2.x":
                version = "Apache/2.2.X"
                print "replaced little x",version
            if version == "Apache/2.0.x":
                version = "Apache/2.0.X"
            if not "coyote" in version.lower() and "apache" in version.lower() and not 'formilux' in version.lower():
                if version.split('/')[1].count('.') == 0:
                    version += ".X.X"
                if version.split('/')[1].count('.') == 1:
                    version += ".X"

            if version == "Apache/2":
                version += ".X.X"


            # check for weirdness
            stdchk = standard_version_regex.match(split_string[1])
            if (stdchk == None and version != "Apache/2") or version == "Apache/" or len(version) < 7: #stop reporting Apache 2
                print "Weirdness alert:",server_string,"read as",version

            # if after all that it doesn't match as desired, give up
            if version == "Apache/":
                version = "unknown"
    else:
        version = "unknown"

    return version

def get_date(version_string, date_dictionary):
    '''
    When given a suitable Apache version string, returns the str release date.
    '''
    return date_dictionary.get(version_string,"n/a")

def load_dates(filename="apache_release_dates.csv"):
    '''
    When given a filename of versions and release dates, returns a dictionary
    with versions as keys and dates as items.

    Assume no header is given, even though it shouldn't matter.
    '''
    dates = {}

    csvfile = file(filename, "r")
    reader = csv.reader(csvfile)

    for row in reader:
        dates[ row[0] ] = row[1]

    return dates


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
    parser.add_argument("-o", nargs=1, help="output file for version counts")
    args = parser.parse_args()

    input = "survey-bottom-10k.csv"
    output = "apache_version_counts.csv"

    if args.i != None: input = args.i[0]
    if args.o != None: output = args.o[0]

    # Read in versions and dates
    apache_versions = load_version_strings(input)
    dates = load_dates()

    # Write version count results
    print apache_versions
    sorted_keys = sorted(apache_versions)

    csvwrite = file(output,"w+")
    writer = csv.writer(csvwrite)
    for server in sorted_keys:
        row = []
        row.append(server)
        row.append(apache_versions[server])
        row.append( get_date(server,dates) )
        print row
        writer.writerow(row)

    csvwrite.close()

if __name__ == "__main__":
    main(sys.argv[1:])
