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
    elif len(idstr) == 0:
        return idstr
    else:
        raise ValueError('Salesforce Ids must be 15 or 18 characters.')


def process_file(input_file, output_file, columns=[], skip_headers=False, progress=None):
    if len(columns) == 0 or type(columns[0]) is int:
        # Numbered columns mode.
        mode = 'index'
        reader = csv.reader(input_file)
        writer = csv.writer(output_file)
    else:
        mode = 'dict'
        reader = csv.DictReader(input_file)
        writer = csv.DictWriter(output_file, fieldnames=reader.fieldnames)

        writer.writeheader()

    bytes_read = 0

    skipped = False
    for row in reader:
        if not skipped and skip_headers and mode == 'index':
            # We're in column-index (non-dictionary) mode
            # Skip the presumable header row.
            skipped = True
            writer.writerow(row)
            bytes_read += sum([len(x) for x in row])
            if progress is not None:
                progress(bytes_read)

            continue

        # Convert the specified columns

        for col in columns:
            row[col] = to18(row[col])

        writer.writerow(row)
        bytes_read += sum([len(x) for x in row])
        if progress is not None:
            progress(bytes_read)
