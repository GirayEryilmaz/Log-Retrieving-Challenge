from os import listdir as ls

import argparse

import bisect

import sys

import dateutil.parser

import os


def parse_date_time(dt_str):
    if not dt_str.strip():
        raise ValueError('Malformed log.')
    return dateutil.parser.parse(dt_str)

def binarySearch(f, min_, max_, target):
    if min_ > max_:
        raise ValueError('Max can not be smaller than Min.')

    result =  _binarySearch(f, min_, max_, target)
    f.seek(0)
    return result

def _binarySearch(f, min_, max_, target):
    while min_ <= max_:
        avg = (min_ + max_) // 2
        f.seek(avg)
        while(True):
            if f.tell() == 0:
                break
            f.seek(f.tell() - 1)
            c = f.read(1)
            if c == '\n':
                break
            else:
                f.seek(f.tell() - 1)
        nextline = f.readline()
        nextdt = parse_date_time(nextline.split(', ')[0])

        if target == nextdt:
            return f.tell() - len(nextline)
        elif target < nextdt:
            if f.tell() - len(nextline) - 1 < 0:
                return 0
            return _binarySearch(f, min_, f.tell() - len(nextline) - 1  , target)
        else:
            if f.tell() > max_:
                return max_
            return _binarySearch(f, f.tell(),max_, target)

def find_file(date_time, log_paths):
    ldt = LazyReadDT(None)
    ldt.dt = date_time

    i = bisect.bisect(log_paths, ldt) - 1        
    if i == -1: i = 0
    return i
     
class LazyReadDT():

    def __init__(self, log_path):
        self.lp = log_path
        self.dt = None

    def __readit__(self):
        with open(self.lp) as l:
            firstdt = l.readline().split(',')[0]
            self.dt = parse_date_time(firstdt)
    
    def __lt__(self, other):
        if self.dt == None:
            self.__readit__()
        
        if other.dt is None:
            other.__readit__() 

        return self.dt < other.dt

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Log Extractor prints logs from given directory within given time period.')

    parser.add_argument('-b', dest='from_time', type=str,
                        default='1970-01-01T00:00:00.0Z',
                        help='starting date time in ISO 8601 format, inclusive')

    parser.add_argument('-e', dest='to_time', type=str,
                        default='3000-01-01T00:00:00.0Z',
                        help='end date time in ISO 8601 format, exclusive')

    parser.add_argument('-d', dest='folder',
                        help='Log file directory location')

    args = parser.parse_args()


    args.from_time = parse_date_time(args.from_time)

    args.to_time = parse_date_time(args.to_time)

    if not args.folder:
        parser.error('Folder must be specified with -d.')



    if args.from_time > args.to_time:
        raise ValueError('"From time" can not be later than "to time".')


    logs = sorted(os.path.join(args.folder,f)  for f in ls(args.folder) if f.startswith('LogFile-'))


    to_search = [ LazyReadDT(log) for log in logs ]


    start_i = find_file(args.from_time, to_search)
    starting_file = logs[start_i]


    end_i = find_file(args.to_time, to_search)
    ending_file = logs[end_i]

    chunk_size = 100000


    if start_i == end_i:
        with open(starting_file) as sf:
            size = os.path.getsize(starting_file)
            start = binarySearch(sf, 0, size-1, args.from_time)
            if start is None:
                print('No logs found')
                sys.exit(0)

            end = binarySearch(sf, 0, size-1, args.to_time)

            sf.seek(start)

            for steps in range((end-start)//chunk_size):
                print(sf.read(chunk_size),end='')
            
            print(sf.read((end-start)%chunk_size),end='')
            
            # the last line is always missed, due to the nature of binarySearch, "end" is where the last log starts not ends
            print(sf.readline(), end='')
            
    else:
        with open(starting_file) as sf:
            size = os.path.getsize(starting_file)
            start = binarySearch(sf, 0, size-1, args.from_time)
            sf.seek(start)
            if start is None:
                print('No logs found')
                sys.exit(0)
            for steps in range((size-start)//chunk_size):
                print(sf.read(chunk_size),end='')
            print(sf.read(), end='')


        curr_file_i = start_i + 1
        while curr_file_i != end_i:
            with open(logs[curr_file_i]) as f:
                for steps in range((size-start)//chunk_size):
                    print(f.read(chunk_size),end='')
                print(f.read(), end='')
                curr_file_i += 1

        with open(ending_file) as ef:
            size = os.path.getsize(ending_file)
            end = binarySearch(ef,0,size-1,args.to_time)


            for steps in range(end//chunk_size):
                print(ef.read(chunk_size),end='')
            
            print(ef.read(end%chunk_size),end='')
            # the last line is always missed, due to the nature of binarySearch, "end" is where the last log starts not ends
            print(ef.readline(),end='')








