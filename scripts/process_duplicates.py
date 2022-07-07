"""
Process duplicates and save then into a JSON file.
"""
import argparse
import json

from collections import defaultdict
from hashlib import sha256

from tqdm import tqdm


def get_args():
    args = argparse.ArgumentParser(
        "Process duplicates"
    )
    args.add_argument("path", help="Dataset filepath")
    args.add_argument("results", help="JSON containing duplicates map")
    args.add_argument("output", help="Output file to save the results")
    args.add_argument(
            "-k", "--keep-filename",
            action='store_true',
            help="Keep filename.")
    return args.parse_args()


def main():
    args = get_args()

    hashes = {}
    mutli_contract_hashes = defaultdict(list)
    results = {
        "hashes": defaultdict(list),
        "addresses": {}
    }
    number_of_slashes = args.path.count('/')
    unique_hashes = set()
    oa_results = {
        "hashes": defaultdict(list),
        "addresses": {}
    }

    print(f"Read {args.results}")
    if not ',' in args.results:
        with open(args.results, 'r') as fp:
            hashes = json.load(fp)
    else:
        hashes = {}
        for r in args.results.split(','):
            with open(r, 'r') as fp:
                h = json.load(fp)
                hashes.update(h)

    print("Get multi contracts and results")
    for filename, value in tqdm(hashes.items()):
        if filename.count('/') == number_of_slashes:
            if not args.keep_filename:
                address = filename.split('/')[-1].replace('.sol', '')
            else:
                address = filename
                only_address = filename.split('/')[-1].replace('.sol', '')
                oa_results['addresses'][only_address] = value
                oa_results['hashes'][value].append(only_address)
            results['addresses'][address] = value
            results['hashes'][value].append(address)
            unique_hashes.add(value)
        else:
            if not args.keep_filename:
                address = filename.split('/')[:number_of_slashes+1][-1].replace('.sol', '')
                only_address = None
            else:
                address = "/".join(filename.split('/')[:-1])
                only_address = filename.split('/')[:number_of_slashes+1][-1].replace('.sol', '')
            mutli_contract_hashes[only_address].append((value, address))

    print("Get hashes for multicontract addesses")
    for address, values in tqdm(mutli_contract_hashes.items()):
        pvalues = [v[0] for v in values]
        full_address = values[0][1]
        concatenated_hash = "".join(pvalues)
        final_hash = sha256(concatenated_hash.encode('utf-8')).hexdigest()
        results['addresses'][full_address] = final_hash
        results['hashes'][final_hash].append(full_address)
        if only_address:
            oa_results['addresses'][address] = final_hash
            oa_results['hashes'][final_hash].append(address)
        unique_hashes.add(final_hash)

    if len(oa_results['hashes'].keys()) > 0:
        print(f"Write {args.output}")
        with open(args.output, 'w') as fp:
            json.dump(oa_results, fp)

        full_paths = args.output.split('.json')[0] + '_full.json'
        print(f"Write {full_paths}")
        with open(full_paths, 'w') as fp:
            json.dump(results, fp)
    else:
        print(f"Write {args.output}")
        with open(args.output, 'w') as fp:
            json.dump(results, fp)

    print()
    print(f"Total unique hashes: {len(unique_hashes)}")


if __name__ == "__main__":
    main()
