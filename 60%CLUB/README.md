## Requirements
- Command Line (i.e linux, terminal, etc)
- Python 2.7
- CSV file for the traffic 
- CSV traffic files must be formatted in a specific way. Please look at the 3 CSV files provided where a 0 represents a SEND request and 1 represents a REQUEST operation.

## Example usage
To run the program on the command line:

> python sim.py -f full/path/to/CSV_Traffic_File

## Help
For more help, run the program with the following argument

> python sim.py --help

## Note
Transaction size is obtained from the tag and index bits

Results from the video may not match up with the documentation because bug fixes
