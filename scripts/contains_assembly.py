"""
Find which contracts contain inline assembly fragments.
"""
import argparse
import os
import json


def get_args():
    parser = argparse.ArgumentParser(
        description='Print contracts containing inline assembly.')
    parser.add_argument(
        "directory", help="Directory that contains the results of the parser."
    )
    parser.add_argument(
        "duplicates", help="JSON file containing duplicates."
    )
    return parser.parse_args()


def find_files(directory):
    """Find json files that need to process"""
    return [os.path.join(directory, f) for f in os.listdir(directory)
            if not f.endswith(".swp")]


def process_json(path):
    """Read JSON files and returns if it has assembly"""
    with open(path, 'r') as infile:
        data = json.load(infile)
    # When we analyze multiple files, then we may get the results for
    # some contracts multiple times. Hence, we want to get all contracts
    # only once.
    contracts = {c: v
                 for f, res in data.items()
                 for c, v in res['contracts'].items()}
    for v in contracts.values():
        if v["stats"]["has_assembly"]:
            return True
    # The contract has assembly only in a comment.
    return False


def process_results(json_files):
    """Read JSON files and compute results"""
    addresses = set()
    for f in json_files:
        address = os.path.basename(f).replace('.json', '')
        has_assembly = process_json(f)
        if has_assembly:
            addresses.add(address)
    return addresses


def main():
    args = get_args()
    json_files = find_files(args.directory)
    with open(args.duplicates) as f:
        duplicates = json.load(f)
    addresses = process_results(json_files)
    contain_assembly = set()
    for addr in addresses:
        addr_hash = duplicates['addresses'][addr]
        duplicated_addresses = duplicates['hashes'][addr_hash]
        contain_assembly.update(duplicated_addresses)
    for addr in contain_assembly:
        print(addr)


if __name__ == "__main__":
    main()
