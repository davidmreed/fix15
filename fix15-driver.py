import fix15
import sys

def main(argv):
    assert len(argv) == 2, 'Usage: fix15-driver input_file.csv > output_file.csv'

    infile = open(argv[1], 'r')

    fix15.process_file(infile, sys.stdout, True)

if __name__ == '__main__':
    main(sys.argv)
