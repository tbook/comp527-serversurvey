# Splits version into tw strings
# Helper to get CSV into a sqlite db
# Handles commas inside quotes
#
# Syntax: csv2tsv infile.csv outfile.tsv

import csv, sys

def main(argv):
    infile = argv[0]
    outfile = argv[1]

    reader = csv.reader(file(infile, "r"))
    writer = csv.writer(file(outfile, 'w+'), delimiter='\t')
    
    header = True
    headerIndices = {} #create a dict for easy lookup
    for row in reader:

        # grab the first row and use it as the header
        if header:
            header = False
            headerRow = row
            serverName = "serverName"
            serverVersion = "serverVersion"
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
            
        #Write the output string
        outRow = []
        for i in range(len(headerRow)):
            if headerRow[i] == 'version':
                outRow.append(serverName)
                outRow.append(serverVersion)
            else:
                outRow.append(row[i])
        writer.writerow(outRow);
        


if __name__ == "__main__":
    main(sys.argv[1:])
