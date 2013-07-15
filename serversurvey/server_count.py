# server_count.py
# 
# Counts number of servers that don't report version and accuracy of our guess.
# Counts false guesses too.

import csv, sys, argparse, math

def main(argv):

    # load file
    parser = argparse.ArgumentParser(description="Tests server")
    parser.add_argument("-f", nargs=1, help="input projections file")
    args = parser.parse_args()

    csvfile = file(args.f[0],"r")

    # read csv with projections
    reader = csv.reader(csvfile,delimiter='\t')    
    headers = reader.next()

    print headers # [1] is Reported, [2] is Guess, [3] is P(guess)

    histogram = {} #boxes of 10% each
    for box in range(90,-10,-10): # 100-90 is box [90]
        histogram[box] = []

    for row in reader:
        reported = row[1]
        guess = row[2]
        
        # check to see if reported server matched our guess
        if reported[:len(guess)].lower() != guess.lower():

            # number reporting false versions with our certainty
            box = float(row[3]) * 100
            box = box - (box % 10)
            box = int(math.floor(box))
            
            if box>=100: box = 90

            histogram[box].append(guess)

        # write to CSV
        outfilename = "lying_servers.tsv"
        outfile = file(outfilename,"w+")
        writer = csv.writer(outfile, delimiter='\t')

        write_headers = ["intervals", "# servers that did not match guess"]
        writer.writerow(write_headers)

        sorted_keys = histogram.keys()
        sorted_keys.sort()
        for minbox in sorted_keys:
            row = []
            row.append(str(minbox) + "-" + str(minbox+10))
            row.append( len(histogram[minbox]) )
            writer.writerow(row)


if __name__ == "__main__":
    main(sys.argv[1:])
