"""
Save all the data retrieved from get_contracts.py script to a single file.
"""
import argparse
import os
import json

from collections import defaultdict
from hashlib import sha256

from tqdm.contrib.concurrent import process_map


def get_args():
    args = argparse.ArgumentParser(
        "Get etherscan data"
    )
    args.add_argument("results", help="Directory containing JSON responses")
    args.add_argument("output", help="Output file to save the results")
    return args.parse_args()


def find_files(directory):
    """Find json files that need to process"""
    return [os.path.join(directory, f) for f in os.listdir(directory)
            if f.endswith(".json")]


def process_directory(filename):
    res = {}
    with open(filename, 'r') as fp:
        address = filename.split('/')[-1].replace('.json', '')
        try:
            r = json.load(fp)
        except:
            print(f"Cannot read: {filename}")
            return {}
        res[address] = {
            'CompilerVersion': r['CompilerVersion'],
            'EVMVersion': r['EVMVersion'],
        }
    return res


def main():
    args = get_args()

    results = {}

    print(f"Check if {args.output} exist")
    if os.path.isfile(args.output):
        with open(args.output, 'r') as f:
            results = json.load(f)

    print(f"Read {args.results}")
    for r in args.results.split(','):
        print(f"Process {r}")
        files = find_files(r)
        res = process_map(process_directory, files, max_workers=4, chunksize=8)
        for d in res:
            results.update(d)

    print(f"Write {args.output}")
    with open(args.output, 'w') as fp:
        json.dump(results, fp)


if __name__ == "__main__":
    main()
