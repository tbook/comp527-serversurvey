# Converts CSV to TSV
# Helper to get CSV into a sqlite db
# Handles commas inside quotes
#
# Syntax: csv2tsv infile.csv outfile.tsv

import csv, sys

def main(argv):
    infile = argv[0]
    outfile = argv[1]

    csv.writer(file(outfile, 'w+'), delimiter='\t').writerows(csv.reader(open(infile)))

if __name__ == "__main__":
    main(sys.argv[1:])
        
