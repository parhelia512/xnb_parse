"""
Dump info from XNB
"""

import sys
import os
import time

from xnb_parse.xnb_reader import XNBReader
from xnb_parse.type_reader_manager import TypeReaderManager


def read_xnb(in_file, type_reader_manager=None):
    print 'Reading %s' % in_file
    with open(in_file, 'rb') as f:
        d = f.read()
    xnb = XNBReader.load(d, type_reader_manager)
    print xnb
    print xnb.content


def main():
    if len(sys.argv) > 1:
        totaltime = time.time()
        type_reader_manager = TypeReaderManager()
        for filename in sys.argv[1:]:
            read_xnb(os.path.normpath(filename), type_reader_manager)
        print '> Done in %.2f seconds' % (time.time() - totaltime)
    else:
        print 'read_xnb.py file1.xnb ...'
