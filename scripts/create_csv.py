"""
Create CSV files to populate a Database.
"""
import argparse
import csv
import os
import json
import statistics
import hashlib
import itertools

from collections import defaultdict

from tqdm import tqdm

from library.assembly_types import OPCODES, OLD_OPCODES, HIGH_LEVEL_CONSTRUCTS, \
    DECLARATIONS, SPECIAL


INSTRUCTION_TYPES = {
        'opcodes': OPCODES, 'old opcodes': OLD_OPCODES,
        'high-level constructs': HIGH_LEVEL_CONSTRUCTS,
        'declarations': DECLARATIONS, 'special opcodes': SPECIAL,
}
TABLE_NAMES = {
        'opcodes': 'Opcode',
        'opcodes frag': 'OpcodesPerFragment',
        'old opcodes': 'OldOpcode',
        'old opcodes frag': 'OldOpcodesPerFragment',
        'high-level constructs': 'HighLevelConstruct',
        'high-level constructs frag': 'HighLevelConstructsPerFragment',
        'declarations': 'Declaration',
        'declarations frag': 'DeclarationsPerFragment',
        'special opcodes': 'SpecialOpcode',
        'special opcodes frag': 'SpecialOpcodesPerFragment',
}
ADDRESS_ID = 1
FILE_ID = 1
CONTRACT_ID = 1
FRAGMENT_ID = 1
PER_FRAGMENT_ID = {instr: 1 for instr in INSTRUCTION_TYPES}
NON_ASSEMBLY_ADDRESS_ID = 1
LABEL_ID = 1
ADDRESS_LABEL_ID = 1
#FIXME TODO
ROWS_LIMIT = 10000


convert_wei = lambda x: int(x) / 1000000000000000000 if x is not None else None
# This will work only on UNIX filesystems
get_address = lambda x: x.split('/')[-1].replace('.json', '')
set_default = lambda x, y: x if x is not None and str(x) != '' else y


def get_args():
    parser = argparse.ArgumentParser(
        description='Create CSV files to populate the database')
    parser.add_argument(
        "contracts", help="CSV file that contains the contracts along with their details"
    )
    parser.add_argument(
        "lines", help="CSV file that contains the LOC of contracts"
    )
    parser.add_argument(
        "duplicates", help="JSON file containing duplicates."
    )
    parser.add_argument(
        "etherscan_data", help="JSON file containing etherscan data."
    )
    parser.add_argument(
        "parser", help="Directory containing parser's analysis results."
    )
    parser.add_argument(
        "output",
        help="Directory to save the results"
    )
    parser.add_argument(
        "-l",
        "--labels",
        help="JSON file containing labels and tags."
    )
    return parser.parse_args()


def find_files(directory):
    """Find json files that need to process"""
    return [os.path.join(directory, f) for f in os.listdir(directory)
            if not f.endswith(".swp")]


def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_file(directory, name, rows):
    path = os.path.join(directory, f"{name}.csv")
    with open(path, 'a') as outfile:
        writer = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(rows)


def get_path_and_name_of_csv(directory, name):
    path = os.path.join(directory, f"{name}.csv")
    return [path, name]


def process_parser_res(address, contracts_lookup, parser_results):
    """Read JSON files"""
    global ADDRESS_ID
    global FILE_ID
    global CONTRACT_ID
    global FRAGMENT_ID
    global PER_FRAGMENT_ID

    # Let it crash if we cannot find the address
    address_data = contracts_lookup[address]
    # ['address_id', 'address', 'nr_transactions', 'unique_callers',
    #  'nr_token_transfers', 'is_erc20', 'is_erc721', 'tvl'
    #  'solidity_version_etherscan', 'evm_version', 'block_number', 'loc',
    #  'hash']
    address_row = [ADDRESS_ID, address] + [None for i in range(11)]
    address_row[2] = set_default(address_data.get('nr_transactions', None),
                                 0)
    address_row[3] = set_default(address_data.get('unique_callers', None),
                                 0)
    address_row[4] = set_default(address_data.get('nr_token_transfers', None),
                                 0)
    address_row[5] = set_default(address_data.get('is_erc20', None), False)
    address_row[6] = set_default(address_data.get('is_erc721', None), False)
    address_row[7] = convert_wei(set_default(address_data.get('tvl', None), 0))
    address_row[8] = address_data.get('CompilerVersion', None)
    address_row[9] = address_data.get('EVMVersion', None)
    address_row[10] = address_data.get('block_number', None)
    address_row[11] = address_data.get('loc', None)
    address_row[12] = address_data.get('hash', None)

    file_rows = []
    contract_rows = []
    fragment_rows = []
    per_fragment_rows = {instr: [] for instr in INSTRUCTION_TYPES}
    for f, values in parser_results.items():
        # This would produce unexpected results if 0x exists before the address.
        file_name = f[f.find('0x'):]
        lines = values['lines']
        solidity_version = values['solidity_version']
        # ['file_id', 'file_name', 'lines', 'address_id']
        file_rows.append([FILE_ID, file_name, lines,
                          solidity_version, ADDRESS_ID])

        for contract, values in values['contracts'].items():
            stats = values['stats']
            lines = stats['lines']
            funcs = stats['funcs']
            funcs_with_assembly = stats['funcs with assembly']
            assembly_fragments = stats['assembly fragments']
            assembly_lines = stats['assembly lines']
            has_assembly = stats['has_assembly']
            # ['contract_id', 'contrac_name','lines', 'funcs',
            #  'funcs_with_assembly', 'assembly_fragments', 'assembly_lines',
            #  'has_assembly', 'file_id']
            contract_rows.append([
                CONTRACT_ID, contract, lines, funcs, funcs_with_assembly,
                assembly_fragments, assembly_lines, has_assembly, FILE_ID])
            for fragment in values['fragments']:
                start_line = fragment['original_lines']['start']['line']
                end_line = fragment['original_lines']['end']['line']
                lines = fragment['lines']
                code = fragment['code']
                # ['fragment_id', 'lines', 'start_line', 'end_line', 'code',
                #  'hash', 'contract_id']
                sha256 = hashlib.sha256(code.encode('utf-8')).hexdigest()
                fragment_rows.append([
                    FRAGMENT_ID, lines, start_line, end_line, code, sha256,
                    CONTRACT_ID
                ])
                for instr, lookup in INSTRUCTION_TYPES.items():
                    for term, occurences in fragment[instr].items():
                        # ['opf_id', 'fragment_id', 'opcode_id', 'occurences']
                        per_fragment_rows[instr].append(
                            [PER_FRAGMENT_ID[instr],
                             FRAGMENT_ID,
                             lookup[term],
                             occurences
                             ]
                        )
                        PER_FRAGMENT_ID[instr] += 1
                FRAGMENT_ID += 1
            CONTRACT_ID += 1
        FILE_ID += 1
    ADDRESS_ID += 1
    return (address_row, file_rows, contract_rows, fragment_rows,
            per_fragment_rows)


def get_non_assembly_rows(address, contracts_lookup):
    """Read JSON files"""
    global NON_ASSEMBLY_ADDRESS_ID
    #table_name = "NonAssemblyAddress"
    address_data = contracts_lookup.get(address, {})
    # ['address_id', 'address', 'nr_transactions', 'unique_callers',
    #  'nr_token_transfers', 'is_erc20', 'is_erc721', 'tvl'
    #  'solidity_version_etherscan', 'evm_version', 'block_number', 'loc',
    #  'hash']
    address_row = [NON_ASSEMBLY_ADDRESS_ID, address] + [None for i in range(11)]
    address_row[2] = set_default(address_data.get('nr_transactions', None), 0)
    address_row[3] = set_default(address_data.get('unique_callers', None), 0)
    address_row[4] = set_default(address_data.get('nr_token_transfers', None),
                                 0)
    address_row[5] = set_default(address_data.get('is_erc20', None), False)
    address_row[6] = set_default(address_data.get('is_erc721', None), False)
    address_row[7] = convert_wei(set_default(address_data.get('tvl', None), 0))
    address_row[8] = address_data.get('CompilerVersion', None)
    address_row[9] = address_data.get('EVMVersion', None)
    address_row[10] = address_data.get('block_number', None)
    address_row[11] = address_data.get('loc', None)
    address_row[12] = address_data.get('hash', None)
    NON_ASSEMBLY_ADDRESS_ID += 1

    return address_row


def get_analysed_address(duplicates, address):
    # We always process the first duplicated address
    addr_hash = duplicates['addresses'].get(address, None)
    if addr_hash is None:
        return None
    return duplicates['hashes'][addr_hash][0]


def get_assembly_path(directory, duplicates, address):
    processed_addr = get_analysed_address(duplicates, address)
    return os.path.join(directory, 'parser', processed_addr + '.json')


def get_parser_results(parser, addresses):
    res = None
    for addr in addresses:
        path = os.path.join(parser, addr + '.json')
        if not os.path.isfile(path):
            continue
        with open(path, 'r') as f:
            res = json.load(f)
        break
    return res


def has_assembly(parser_res):
    if parser_res is None:
        return False
    for files in parser_res.values():
        for contract in files['contracts'].values():
            if contract['stats']['has_assembly']:
                return True
    return False


def process_results(output, contracts_lookup, duplicates, parser):
    """Read JSON files and create CSV files."""
    addresses_rows = []
    files = []
    contracts = []
    fragments = []
    per_fragments = {instr: [] for instr in INSTRUCTION_TYPES}
    non_assembly_addresses = []
    create_dir(output)

    for _, addresses in tqdm(duplicates['hashes'].items()):
        parser_results = get_parser_results(parser, addresses)
        is_assembly_address = has_assembly(parser_results)

        if is_assembly_address:
            # get assembly rows
            for address in addresses:
                process_json_res = process_parser_res(
                    address, contracts_lookup, parser_results)

                if process_json_res is None:
                    print(f"Error: Could not process {address}")
                    continue
                (address_row, file_rows, contract_rows,
                 fragment_rows, per_fragment_rows
                 ) = process_json_res
                addresses_rows.append(address_row)
                files.extend(file_rows)
                contracts.extend(contract_rows)
                fragments.extend(fragment_rows)
                for instr, rows in per_fragment_rows.items():
                    per_fragments[instr].extend(rows)

                # If more than 10k addresses save and clean
                if len(addresses_rows) > ROWS_LIMIT:
                    save_file(output, 'Address', addresses_rows)
                    addresses_rows = []
                    save_file(output, 'SolidityFile', files)
                    files = []
                    save_file(output, 'Contract', contracts)
                    contracts = []
                    save_file(output, 'Fragment', fragments)
                    fragments = []
                    for instr, rows in per_fragments.items():
                        save_file(output, TABLE_NAMES[instr + ' frag'], rows)
                        per_fragments[instr] = []
        else:
            for address in addresses:
                non_assembly_rows = get_non_assembly_rows(
                    address, contracts_lookup
                )
                non_assembly_addresses.append(non_assembly_rows)
                if len(non_assembly_addresses) > ROWS_LIMIT:
                    save_file(output, 'NonAssemblyAddress',
                              non_assembly_addresses)
                    non_assembly_addresses = []

    save_file(output, 'NonAssemblyAddress',
              non_assembly_addresses)
    save_file(output, 'Address', addresses_rows)
    save_file(output, 'SolidityFile', files)
    save_file(output, 'Contract', contracts)
    save_file(output, 'Fragment', fragments)
    for instr, rows in per_fragments.items():
        save_file(output, TABLE_NAMES[instr + ' frag'], rows)

    results = []
    results.append(get_path_and_name_of_csv(output, 'NonAssemblyAddress'))
    results.append(get_path_and_name_of_csv(output, 'Address'))
    results.append(get_path_and_name_of_csv(output, 'SolidityFile'))
    results.append(get_path_and_name_of_csv(output, 'Contract'))
    results.append(get_path_and_name_of_csv(output, 'Fragment'))
    for instr, rows in per_fragments.items():
        results.append(get_path_and_name_of_csv(
            output, TABLE_NAMES[instr + ' frag']))
    return results


def create_instruction_tables_csv(output):
    # ['instruction_id', 'instruction_name']
    results = []
    for instr, instructions in INSTRUCTION_TYPES.items():
        save_file(output, TABLE_NAMES[instr],
                  [[inst_id, inst] for inst, inst_id in instructions.items()])
        results.append(get_path_and_name_of_csv(output, TABLE_NAMES[instr]))
    return results


def process_labels_json(path, output):
    global LABEL_ID
    global ADDRESS_LABEL_ID
    labels_name = "Label"
    address_label_name = "AddressLabel"
    # ['label_id', 'label_name']
    labels_rows = []
    # ['al_id', 'label_id', 'address', 'address_type', 'tag']
    address_label_rows = []

    with open(path, 'r') as infile:
        data = json.load(infile)

    for label, label_values in data.items():
        labels_rows.append([LABEL_ID, label])
        for addr_type, addresses in label_values.items():
            for address, tag in addresses.items():
                address_label_rows.append([
                    ADDRESS_LABEL_ID, LABEL_ID, address, addr_type, tag
                ])
                ADDRESS_LABEL_ID += 1
        LABEL_ID += 1

    save_file(output, labels_name, labels_rows)
    save_file(output, address_label_name, address_label_rows)
    label_file = get_path_and_name_of_csv(output, labels_name)
    address_label_file = get_path_and_name_of_csv(output, address_label_name)
    return [label_file, address_label_file]


def create_populate_script(output, results):
    path = os.path.join(output, 'populate.sql')
    lines = [".mode csv\n"] + [
        f".import {path} {name}\n"
        for path, name in results
    ]
    with open(path, 'w') as f:
        f.writelines(lines)


def get_addresses(directory):
    assembly_contracts = os.path.join(directory, 'assembly_contracts.csv')
    with open(assembly_contracts, 'r') as f:
        reader = csv.reader(f)
        assembly_contracts = [r[0] for r in reader]
    non_assembly_contracts = os.path.join(directory,
                                          'non_assembly_contracts.csv')
    with open(non_assembly_contracts, 'r') as f:
        reader = csv.reader(f)
        non_assembly_contracts = [r[0] for r in reader]
    return assembly_contracts, non_assembly_contracts


def main():
    args = get_args()
    print("Read LOC")
    with open(args.lines, 'r') as f:
        reader = csv.reader(f, delimiter=",")
        lines = {row[0].split('/')[-1].replace('.sol', ''): int(row[1])
                 for row in reader}
    print("Read Duplicates")
    with open(args.duplicates, 'r') as f:
        duplicates = json.load(f)
    print("Read etherscan data")
    with open(args.etherscan_data, 'r') as f:
        etherscan_data = json.load(f)
    print("Read Address Metadata")
    with open(args.contracts, 'r') as f:
        # address,tx_count,unique_callers,token_transfers,balance,is_erc20,
        # is_erc721,block_number,loc,hash
        reader = csv.reader(f, delimiter=",")
        # Skip headers
        row = next(reader)
        if row[0] != 'address':
            reader = itertools.chain([row], reader)
        contracts = {}
        for row in tqdm(reader):
            contracts[row[0]] = {
                'nr_transactions': row[1], 'unique_callers': row[2],
                'nr_token_transfers': row[3], 'tvl': row[4],
                'is_erc20': row[5], 'is_erc721': row[6],
                'block_number': row[7],
                'loc': lines.get(get_analysed_address(duplicates, row[0]), None),
                'hash': duplicates['addresses'].get(row[0], None),
                'CompilerVersion': etherscan_data.get(
                    row[0], {'CompilerVersion': None})['CompilerVersion'],
                'EVMVersion': etherscan_data.get(
                    row[0], {'EVMVersion': None})['EVMVersion']
            }
    del lines
    del etherscan_data
    print("Process results (duplicates)")
    results = process_results(args.output, contracts, duplicates, args.parser)
    results.extend(create_instruction_tables_csv(args.output))
    if args.labels:
        print("Process Labels")
        results.extend(process_labels_json(args.labels, args.output))
    print("Save results")
    create_populate_script(args.output, results)


if __name__ == "__main__":
    main()
