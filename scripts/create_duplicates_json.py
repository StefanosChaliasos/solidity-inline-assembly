#!/usr/bin/env python3
"""
Read from STDIN and create a JSON file.
"""
import fileinput
import json
import sys


result = {
}

for line in fileinput.input():
    try:
        striped = line.strip().split(' ')
        sha256 = striped[0]
        if len(striped) > 2:
            # Then there is a space in the filename; thus, we will replace it
            # with n underscore.
            filename = "_".join(striped[1:])
        else:
            filename = line.strip().split(' ')[1]
    except Exception as ex:
        print("-----")
        print("line:", ex, file=sys.stderr)
        print("Exception:", ex, file=sys.stderr)
        print("-----")
    result[filename] = sha256

print(json.dumps(result))
