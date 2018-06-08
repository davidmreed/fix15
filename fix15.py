import celery
import flask
import csv

def to18(idstr):
    if len(idstr) == 15:
        # To construct the 18 character Salesforce id, we're going to build a 15-bit checksum
        # expressed as three alphanumeric characters.
        # We do this by constructing 3 five-bit indices into the alnum character range
        # Each five-bit index corresponds to the case (1 = uppercase) of five characters
        # of the 15-digit Salesforce Id, in reverse order (LSB is the first character)

        # Build up a bitstring
        bitstring = 0
        for i in range(0, 15):
            if idstr[i] >= 'A' and idstr[i] <= 'Z':
                bitstring |= 1 << i

        # Take three slices of the bitstring and use them as 5-bit indices into the alnum sequence.
        alnums = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ012345'
        return idstr + alnums[bitstring & 0x1F] + alnums[bitstring>>5 & 0x1F] + alnums[bitstring>>10]
    elif len(idstr) == 18:
        return idstr
    else:
        raise ValueError('Salesforce Ids must be 15 or 18 characters.')


def is_salesforce_id(string):
    return string.isalnum() and (len(string) == 18 or len(string) == 15)

def process_file(input_file, output_file, skip_headers = True, progress = None):
    statuses = []
    reader = csv.reader(input_file)
    writer = csv.writer(output_file)
    bytes_written = 0

    skipped = False
    for row in reader:
        if not skipped and skip_headers:
            skipped = True
            writer.writerow(row)
            bytes_written += sum([len(x) for x in row])
            if progress is not None:
                progress(bytes_written)

            continue
        
        if len(statuses) == 0:
            statuses = [None for i in range(0, len(row))]
        
        # scan for Salesforce Ids in this row
        # statuses is a kind of pseudo-map: we scan the incoming data for values that
        # look like Ids. If we find one, we put True in statuses[that_index]
        # If we find a value that's clearly not a Salesforce Id, we put False
        # None means we haven't yet determined the nature of the column.

        for (i, value) in enumerate(row):
            if statuses[i] is None:
                if is_salesforce_id(value):
                    statuses[i] = True

            if statuses[i]:
                # Transform this value
                row[i] = to18(value)

        writer.writerow(row)
        bytes_written += sum([len(x) for x in row])
        if progress is not None:
            progress(bytes_written)
