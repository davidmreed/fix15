# fix15

This tool aims to simplify Salesforce data-load and ETL workflows by seamlessly converting 15-character Id values to their corresponding 18-character Ids in CSV data. 

## Usage

> cat test.csv | fix15 -c Id -c AccountId > done.csv

Converts the columns "AccountId" and "Id" in the file test.csv and writes the output to done.csv.

> fix15 -c Id -c AccountId -i test.csv -o done.csv

Exactly the same as above.

> fix15 -n 0 -n 4 -s -i test.csv -o done.csv 

Converts the first (0-based) and fifth columns of test.csv, skipping a header row (-s). Omit -s if no header row is present; this ensures that in numbered-column mode no error is thrown for header values, which are not valid Ids.

## Caveats

fix15 only handles CSV files encoded in UTF-8, which is an option when exporting report data from Salesforce. HTML-formatted ("xls") Salesforce report exports are *not* supported.