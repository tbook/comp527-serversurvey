# apache_versions.py
#
# Counts Apache version strings.

import csv,sys,argparse
import re
from operator import itemgetter

# globals #
version_regex = re.compile("\d+([.][0-9xX]+)*")

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
    parser.add_argument("-o", nargs=1, help="output file for version counts")
    args = parser.parse_args()

    input = "survey-bottom-10k.csv"
    output = "apache_version_counts.csv"

    if args.i != None: input = args.i[0]
    if args.o != None: output = args.o[0]

    # Read in versions
    apache_versions = load_version_strings(input)

    # Write version count results
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
