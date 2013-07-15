"""
Divides a list into two sets - designed
to split data into a training set and an experimental set
"""
import sys,csv

if __name__ == '__main__':
    if len(sys.argv) < 4:
        sys.stderr.write("\nSplit a data set into two, by site.")
        sys.stderr.write("\nSyntax: splitSample.py [source file] [outputfile1] [outputfile2]\n\n")
        sys.exit(1)

    sourceFileName = sys.argv[1]
    destFileName0 = sys.argv[2]
    destFileName1 = sys.argv[3]

    sourceFile = open(sourceFileName, 'r')
    destFile0 = open(destFileName0, 'w')
    destFile1 = open(destFileName1, 'w')

    sourceReader = csv.reader(sourceFile)
    destWriter0 = csv.writer(destFile0)
    destWriter1 = csv.writer(destFile1)

    header = sourceReader.next()
    destWriter0.writerow(header)
    destWriter1.writerow(header)

    dest0Hosts = set()
    dest1Hosts = set()
    currentDest = 0
    count = 0

    for response in sourceReader :
        count = count + 1
        host = response[0]
        if host in dest0Hosts :
            dest = 0
        elif host in dest1Hosts :
            dest = 1
        elif currentDest == 0 :
            dest = 0
            dest0Hosts.add(host)
            currentDest = 1
        else :
            dest = 1
            dest1Hosts.add(host)
            currentDest = 0

        if dest == 0 :
            destWriter0.writerow(response)
        else :
            destWriter1.writerow(response)

    print str(count) + " rows processed"
    print str(len(dest0Hosts) + len(dest1Hosts)) + " hosts found"
    print str(len(dest0Hosts)) + " hosts written to " + destFileName0
    print str(len(dest1Hosts)) + " hosts written to " + destFileName1