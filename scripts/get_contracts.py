"""
Use the API of Etherscan to get the source code of contracts
"""
import os
import json
import sys
import argparse
import time

from etherscan.contracts import Contract


def get_args():
    args = argparse.ArgumentParser(
        "Get the source code of contracts from Etherscan"
    )
    args.add_argument("api_key", help="API Key for Etherscan")
    args.add_argument("contracts", help="CSV file with contract addresses")
    args.add_argument(
        "--dataset",
        default="data/contracts",
        help="Directory to save contracts' sources (default: 'data/contracts')"
    )
    args.add_argument(
        "--invalid",
        default="data/logs/invalid.json",
        help="JSON file to save error messages"
    )
    args.add_argument(
        "--dry",
        action='store_true',
        help="Do not crawl new data"
    )
    return args.parse_args()


def read_contracts(contracts):
    with open(contracts, 'r') as fp:
        return [line.split(',')[0] for line in fp.readlines() 
                if 'address' not in line]


def create_read_dataset(dataset):
    dataset_json = os.path.join(dataset, 'json')
    dataset_sources = os.path.join(dataset, 'sol')
    os.makedirs(dataset_json, exist_ok=True)
    os.makedirs(dataset_sources, exist_ok=True)
    all_contracts = [f for f in os.listdir(dataset_json)]
    only_sources = [f for f in os.listdir(dataset_sources)]
    return all_contracts, only_sources


def create_read_invalid(invalid):
    directory = os.path.dirname(invalid)
    if os.path.exists(invalid):
        with open(invalid) as fd:
            return json.load(fd)
    os.makedirs(directory, exist_ok=True)
    return {} 


def crawl_contracts(contracts, dataset_dir, token, invalid, invalid_src):
    def print_msg():
        template_msg = (u"Addresses processed {} / {} \u2714\t"
                         "Succeed             {} / {} \u2714\t"
                         "Empty               {} / {} \u2714\t"
                         "Invalid             {} / {} \u2718\r")
        sys.stdout.write('\033[2K\033[1G')
        msg = template_msg.format(
            count, len(contracts),
            count_new - count_empty - count_invalid, count_new,
            count_empty, count_new,
            count_invalid, count_new
        )
        sys.stdout.write(msg)

    def check_time():
        if time.time() - start >= 1:
            if requests >= 4:
                time.sleep(1)
            return 0, time.time()
        return requests, start

    count = 0
    count_new = 0
    count_empty = 0
    count_invalid = 0

    # we should not perform more than 5 requests per second
    requests, start = 0, time.time()

    print()
    for address in contracts:
        address = address.strip()
        print_msg()
        count += 1
        if address in invalid:
            continue
        contract_path = os.path.join(dataset_dir, 'json', address + '.json')
        if os.path.exists(contract_path):
            continue
        count_new += 1
        try:
            requests += 1
            requests, start = check_time()
            api = Contract(address=address, api_key=token)
            sourcecode = api.get_sourcecode()
            if len(sourcecode[0]['SourceCode']) == 0:
                count_empty += 1
            else:
                filename = os.path.join(dataset_dir, 'sol', address + '.sol')
                with open(filename, 'w') as fd:
                    fd.write(sourcecode[0]['SourceCode'])
            with open(contract_path, 'w') as fd:
                json.dump(sourcecode[0], fd)
                
        except Exception as err:
            invalid[address] = str(err)
            with open(invalid_src, 'w') as fd:
                json.dump(invalid, fd, indent=4)
            count_invalid += 1
    print_msg()
    print()
    print()

    print((f"Total      {len(contracts)}\n"
           f"New        {count_new}\n"
           f"Succeed    {count_new - count_empty - count_invalid}\n"
           f"Empty      {count_empty}\n"
           f"Invalid    {count_invalid}"))


def main():
    args = get_args()
    token = args.api_key
    contracts = args.contracts
    dataset_dir = args.dataset
    invalid_src = args.invalid

    # Addresses to crawl
    addresses = read_contracts(contracts)
    # Read invalid.json
    invalid = create_read_invalid(invalid_src)
    # Contracts for which we already have their sources
    dataset_all, dataset_sources = create_read_dataset(dataset_dir)

    nr_contracts = len(addresses)

    print(f"Etherscan API Key      {token}")
    print(f"Nr of contracts        {nr_contracts}")
    print(f"Contracts processed    {len(dataset_all)}")
    print(f"Dataset                {dataset_dir} -- {len(dataset_sources)}")

    if not args.dry:
        crawl_contracts(addresses, dataset_dir, token, invalid, invalid_src)


if __name__ == "__main__":
    main()
