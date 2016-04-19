#!/usr/bin/python

import os

if __name__ == '__main__':
    print('PATH_INFO: {}'.format(os.environ['PATH_INFO']))
    print('QUERY_STRING: {}'.format(os.environ['QUERY_STRING']))

