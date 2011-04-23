#!/usr/bin/env python

import csv
import os

_file = 'equipmentcode'
_lines = csv.reader(open(_file, 'r'))
lookupTable = {}

def getName(code):
    return Equipment.lookupTable[str(code)]

for _line in _lines:
    _code = _line[0]
    _value = _line[1]
    lookupTable[_code] = _value