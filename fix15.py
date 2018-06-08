import celery
import flask
import csv

class SalesforceId(object):
    def __init__(self, idstr):
        if len(idstr) == 15:
            suffix = ''
            for i in range(0, 3):
                baseTwo = 0
                for j in range (0, 5):
                    character = idstr[i*5+j]
                    if character >= 'A' and character <= 'Z':
                        baseTwo += 1 << j
                suffix += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ012345'[baseTwo]
            self.id = idstr + suffix
        elif len(idstr) == 18:
             self.id = idstr
        else:
            raise ValueError('Salesforce Ids must be 15 or 18 characters.')
   
    def __eq__(self, other):
        if isinstance(other, SalesforceId):
            return self.id == other.id
        elif isinstance(other, str):
            return self.id == SalesforceId(other).id
        
        return False
    
    def __hash__(self):
        return hash(self.id)
   
    def __str__(self):
        return self.id
    
    def __repr__(self):
        return 'Salesforce Id: ' + self.id

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
                row[i] = SalesforceId(value)

        writer.writerow(row)
        bytes_written += sum([len(x) for x in row])
        if progress is not None:
            progress(bytes_written)
