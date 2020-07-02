The scenario:
There are many log-dump files each size of ~20 Gigabytes.
Logs are plain text in the following format:
    <ISO 8601 format time stamp>, <log item1>, <log item2>, ...\n
An example is:
    "2020-06-29T08:24:55.490754Z, Field One, Field Two, Field 3\n"
    
Logs are sorted according to the time stamps, and a script for bringing logs from a given time period is needed every once in a while.
This operation needs to be fast.

There are 3 flag for the script; 
    -d for the directory where the log files reside
    -b for the beginning of the time interval (inclusive)
    -e for the end of the time interval (inclusive)

Usage example:
    python3 LogExtractor.py -d ./ -b 2020-06-29T08:24:55.612615Z -e 2020-06-29T08:24:55.612631Z

For efficiency, the script first finds the beginning time and end time in the logs using two binary searches.
Then does another pair of binary searches in those file(s) to find exact locations of the first and the last log to retrieve.
Finally prints all the logs between in chunks to achieve maximum speed without running out of memory.
You can play with the chunk size to see how much it affects running time.
