"""
Split sol files retrieved from etherscan that contain multiple sources to 
many files.
"""
import os
import json
import sys
import argparse
import time

from pathlib import Path

from tqdm.contrib.concurrent import process_map


def get_args():
    args = argparse.ArgumentParser(
        "Split sol files that contain multiple contracts to many files in a single directory."
    )
    args.add_argument("directory", help="Directory to search")
    args.add_argument("--workers", type=int, default=2,
                      help="Number of processes to use")
    return args.parse_args()


def get_json(filename):
    try:
        with open(filename, 'r') as f:
            res = json.loads(f.read())
            return filename, res
    except ValueError:
        # Probably the file starts with {{ and ends with }}
        try:
            txt = Path(filename).read_text()
            txt = txt[1:]
            txt = txt[:-1]
            res = json.loads(txt)
            return filename, res
        except Exception:
            # Then probably the file is a normal source code file
            # No other actions need to be made
            pass
        return None


def handle_json(args):
    filename, json_obj = args
    os.remove(filename)
    os.mkdir(filename)
    for name, contents in json_obj.items():
        name = name.split('/')[-1]
        if '.sol' in name:
            with open(os.path.join(filename, name), 'w') as f:
                f.write(contents['content'])
    for name, contents in json_obj.get("sources", {}).items():
        name = name.split('/')[-1]
        if '.sol' in name:
            with open(os.path.join(filename, name), 'w') as f:
                f.write(contents['content'])


def main():
    args = get_args()
    directory = args.directory

    print("Find Files")
    files = [os.path.join(directory, f) for f in os.listdir(directory)
             if os.path.isfile(os.path.join(directory, f))]
    print(f"Nr of files: {len(files)}")
    print("Get JSON files")
    json_files = process_map(get_json, files, max_workers=args.workers,
                             chunksize=args.workers*2)
    print("Filter JSON files")
    json_files = list(filter(lambda x: x is not None, json_files))
    print(f"Nr of JSON files: {len(json_files)}")
    process_map(handle_json, json_files, max_workers=args.workers,
                chunksize=args.workers)


if __name__ == "__main__":
    main()
