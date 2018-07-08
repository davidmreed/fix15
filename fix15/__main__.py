import sys
import argparse
from fix15 import process_file

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--column',
                        dest='column_names',
                        action='append',
                        type=str,
                        help='The name of a column to be converted from a 15 to 18 character Salesforce Id')
    parser.add_argument('-n', '--column-index',
                        dest='column_indices',
                        action='append',
                        type=int,
                        help='The index (starting with 0) of a column to be converted from a 15 to 18 character Salesforce Id')
    parser.add_argument('-i', '--input',
                        dest='infile',
                        type=argparse.FileType('r'),
                        default=sys.stdin,
                        help='The input file. The default is standard input.')
    parser.add_argument('-o', '--output',
                        dest='outfile',
                        type=argparse.FileType('w'),
                        default=sys.stdout,
                        help='The output file. The default is standard output.')
    parser.add_argument('-s', '--skip-headers',
                        dest='skip_headers',
                        action='store_true',
                        default=True,
                        help='Skip over a header row, if using column indices rather than names.')

    a = parser.parse_args()

    if a.column_indices is not None and len(a.column_indices) > 0:
        columns = a.column_indices
    elif a.column_names is not None and len(a.column_names) > 0:
        columns = a.column_names
    else:
        parser.print_usage()
        exit(-1)

    process_file(a.infile,
                 a.outfile,
                 columns=columns,
                 skip_headers=a.skip_headers)
    
    return 0

if __name__ == '__main__':
    exit(main())