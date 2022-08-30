"""
Perform queries to the inline assembly sqlite3 database.
"""
import argparse
import os
import json
import statistics
import sqlite3
import sys

from collections import defaultdict
from functools import reduce

import pandas as pd

from library.assembly_types import OPCODES, OLD_OPCODES, \
    HIGH_LEVEL_CONSTRUCTS, DECLARATIONS, SPECIAL
from library.taxonomy import ARITHMETIC_OPERATIONS, COMPARISON_BITWISE, \
    HASH_OPERATIONS, ENVIROMENTAL_INFORMATION, BLOCK_INFORMATION, \
    STACK_MEMORY_STORAGE, FLOW_OPERATIONS, PUSH_DUP_SWAP, LOGGING_OPERATIONS, \
    YUL_DECLARATIONS, YUL_SPECIAL_INSTRUCTIONS, SYSTEM_OPERATIONS
from library.plots import plot_signle_line, plot_histogram_tweaked, useplot
from library.queries import QUERIES


INSTRUCTIONS = {
    'opcode': ('OpcodesPerFragment', 'Opcode'),
    'old_opcode': ('OldOpcodesPerFragment', 'OldOpcode'),
    'high_level_construct': ('HighLevelConstructsPerFragment', 'HighLevelConstruct'),
    'declaration': ('DeclarationsPerFragment', 'Declaration'),
    'special_opcode': ('SpecialOpcodesPerFragment', 'SpecialOpcode'),
}


def pretty_num(num):
    if isinstance(num, str):
        return num
    if int(num) > 100000000000:
        return "{}.{} B".format(str(num)[:3], str(num)[3])
    if int(num) > 10000000000:
        return "{}.{} B".format(str(num)[:2], str(num)[2])
    if int(num) > 1000000000:
        return "{}.{} B".format(str(num)[0], str(num)[1])
    if int(num) > 100000000:
        return "{}.{} M".format(str(num)[:3], str(num)[3])
    if int(num) > 10000000:
        return "{}.{} M".format(str(num)[:2], str(num)[2])
    if int(num) > 1000000:
        return "{}.{} M".format(str(num)[0], str(num)[1])
    if int(num) > 100000:
        return "{}.{} K".format(str(num)[:3], str(num)[3])
    if int(num) > 10000:
        return "{}.{} K".format(str(num)[:2], str(num)[2])
    if int(num) > 1000:
        return "{}.{} K".format(str(num)[0], str(num)[1])
    if int(num) > 100:
        return int(num)
    return num if int(num) == num else "{:.2f}".format(num)


def null_to_zero(num):
    return num if num is not None and num != '' else 0.0


def get_perc(a, b, precision=0):
    if precision == 0:
        return int((a/b) * 100)
    if b == 0:
        return 0
    return float('{:.{precision}}'.format((a/b) * 100, precision=precision))


def get_compiler_version(version):
    res = version[:version.find('-')]
    res = res[:res.find('+')]
    return res.replace('v', '')


def create_dirs(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def connect(db):
    return sqlite3.connect(db)


def run_query(con, query, params=None, filters={}):
    cur = con.cursor()

    if len(filters) == 0:
        q = QUERIES[query]
    else:
        q = QUERIES[query + '_filtered']

    if params is not None:
        if not isinstance(params, dict):
            raise Exception("params should be dict")

    if len(filters) > 0 and params:
        q = q.format(**filters, **params)
    elif len(filters) > 0:
        q = q.format(**filters)
    elif params:
        q = q.format(**params)

    res = cur.execute(q)
    return res


def process_res(res, res_type):
    if res_type == 'value':
        return next(res)[0]
    elif res_type == 'values':
        return [r[0] for r in res]
    elif res_type == 'tuples':
        return [r for r in res]
    else:
        raise Exception(f"Unknown res_type: {res_type}")


def get_stats(data):
    data = [int(i) for i in data if i is not None and str(i) != '']
    try:
        return {
            "total": sum(i for i in data),
            "max": max(data),
            "min": min(data),
            "mean": statistics.mean(data),
            "median": statistics.median(data),
            "sd": statistics.stdev(data)}
    except statistics.StatisticsError:
        return {
            "total": sum(i for i in data),
            "max": max(data),
            "min": min(data),
            "mean": statistics.mean(data),
            "median": statistics.median(data),
            "sd": 0}
    except ValueError:
        data = [0]
        return {
            "total": sum(i for i in data),
            "max": max(data),
            "min": min(data),
            "mean": statistics.mean(data),
            "median": statistics.median(data),
            "sd": 0}


def convert_tuples_to_dict(tuples):
    """
        gas|1, mload|2, add|1, mload|1
        =>
        {'gas': [1], 'mload': [2,1], 'add': [1]
    """
    res = defaultdict(list)
    for term, value in tuples:
        res[term].append(value)
    return res


def get_stats_instr(total_addresses, data):
    """Get a dict of lists and generate a dict of dicts
        {'opcode': {'percentage': 0.1, 'occ': 3, 'total': 10}}
    """
    return {instr: {'perc': get_perc(len(values), total_addresses, 4),
                     'occ': len(values),
                     'total': sum(values)}
             for instr, values in data.items()}


def print_res(title, res, style, first_col=35):
    if style == 'simply':
        if isinstance(res, dict):
            res = ", ".join(f"{k} ({v})" for k, v in res.items())
        print(f"{title}: {res}")
    elif style == 'table':
        # res should be a dict of dict in the following format:
        # {"row name": {"column name": value, ...}, ...}
        def print_line(title, columns, values):
            row_format = f"{{:<{first_col}}}" + "{:>12}" * len(columns)
            print(row_format.format(
                title,
                *(pretty_num(values[column]) for column in columns)
            ))
        if len(res.values()) == 0:
            return
        header = [""] + list(list(res.values())[0].keys())
        row_format = f"{{:<{first_col}}}" + "{:>12}" * (len(header) - 1)
        lenght = first_col + 12 * (len(header) - 1)
        print(title.center(lenght))
        print(lenght * "=")
        print(row_format.format(*header))
        print(lenght * "-")
        for row_name, values in res.items():
            print_line(row_name, header[1:], values)
        print()
    else:
        raise Exception(f"Unknown style: {style}")


def get_addresses(con, filters={}):
    without_addresses = process_res(
        run_query(con, 'non_inline_addresses', filters=filters), 'value'
    )
    assembly_addresses = process_res(
        run_query(con, 'total_addresses', filters=filters), 'value'
    )
    total_addresses = without_addresses + assembly_addresses
    return without_addresses, assembly_addresses, total_addresses


def get_unique_addresses(con, filters={}):
    without_addresses = process_res(
        run_query(con, 'non_inline_addresses_unique'), 'value'
    )
    assembly_addresses = process_res(
        run_query(con, 'total_addresses_unique'), 'value'
    )
    total_addresses = without_addresses + assembly_addresses
    return without_addresses, assembly_addresses, total_addresses


def print_total_addresses(con):
    without_addresses, assembly_addresses, total_addresses = get_addresses(con)
    print_res("Total addresses", total_addresses, 'simply')
    print_res("Total addresses with assembly", assembly_addresses, 'simply')
    print_res("Total addresses without assembly", without_addresses, 'simply')


def print_sources_statistics(con, total_contracts, latex=False, filters={}):
    title = 'Source statistics'
    print_rq_question(title)
    if len(filters) > 0:
        print("Warning: when using filters the results are not correct")
    _, assembly_contracts, total_addresses_with = get_addresses(con, filters)
    total_addresses_with_perc = get_perc(total_addresses_with, total_contracts)
    total_addresses_without = total_contracts - total_addresses_with
    total_addresses_without_perc = get_perc(total_addresses_without,
                                            total_contracts)
    _, _, total_unique_contracts = get_unique_addresses(con, filters)
    total_unique_contracts_perc = get_perc(total_unique_contracts,
                                           total_addresses_with)
    total_duplicate_contracts = total_addresses_with - total_unique_contracts
    non_loc = process_res(
        run_query(con, 'total_loc',
                  {'table': 'NonAssemblyAddress'}, filters=filters),
        'value'
    )
    with_loc = process_res(
        run_query(con, 'total_loc',
                  {'table': 'Address'}, filters=filters), 'value'
    )
    non_loc_unique = process_res(
        run_query(
            con, 'total_loc_from_unique',
            {'table': 'NonAssemblyAddress'}, filters=filters
        ), 'value'
    )
    with_loc_unique = process_res(
        run_query(con, 'total_loc_from_unique',
                  {'table': 'Address'}, filters=filters),
        'value'
    )

    loc = int(non_loc + with_loc)
    loc_unique = int(non_loc_unique + with_loc_unique)
    print(80*"-")
    print("Solidity source available: {} ({}%)".format(
        total_addresses_with, total_addresses_with_perc
    ))
    print("Solidity source not available: {} ({}%)".format(
        total_addresses_without, total_addresses_without_perc
    ))
    print(f"LOC: {loc}")
    print(80*"-")
    print("Unique Solidity Contracts: {} ({}%)".format(
        total_unique_contracts, total_unique_contracts_perc
    ))
    print(f"LOC of Unique Solidity Contracts: {loc_unique}")
    print(80*"-")
    if latex:
        print(":::::LATEX:::::")
        print_latex("contractsprocessed",
                    pretty_num(total_contracts),
                    use_num=False
        )
        print_latex("contractswithsolidity",
                    pretty_num(total_addresses_with),
                    use_num=False
        )
        print_latex("contractswithoutsolidity",
                    pretty_num(total_addresses_without),
                    use_num=False
        )
        print_latex("contractswithsolidityperc",
                    pretty_num(total_addresses_with_perc), '\\%',
                    use_num=False
        )
        print_latex("contractswithoutsolidityperc",
                    pretty_num(total_addresses_without_perc), '\\%',
                    use_num=False
        )
        print_latex("contractsloc",
                    pretty_num(loc),
                    use_num=False
        )
        print_latex("uniquecontracts",
                    pretty_num(total_unique_contracts),
                    use_num=False
        )
        print_latex("uniquecontractsperc",
                    pretty_num(total_unique_contracts_perc), '\\%',
                    use_num=False
        )
        print_latex("uniquecontractsloc",
                    pretty_num(loc_unique),
                    use_num=False
        )
        print_latex("duplicatecontracts",
                    pretty_num(total_duplicate_contracts),
                    use_num=False
        )
        print_latex("assemblycontracts",
                    pretty_num(assembly_contracts),
                    use_num=False
        )
        print(":::::::::::::::")


def print_statistics(con, filters):
    # General statistics
    files_per_address = process_res(
        run_query(con, 'files_per_address', filters=filters), 'values'
    )
    lines_per_address = process_res(
        run_query(con, 'lines_per_address', filters=filters), 'values'
    )
    contracts_per_address = process_res(
        run_query(con, 'contracts_per_address', filters=filters), 'values'
    )
    functions_per_address = process_res(
        run_query(con, 'functions_per_address', filters=filters), 'values'
    )
    functions_with_assembly_per_address = process_res(
        run_query(con, 'functions_with_assembly_per_address',
                  filters=filters), 'values'
    )
    assembly_lines_per_address = process_res(
        run_query(con, 'assembly_lines_per_address', filters=filters), 'values'
    )
    fragments_per_address = process_res(
        run_query(con, 'fragments_per_address', filters=filters), 'values'
    )
    general_stats = {
        "Files per address": get_stats(files_per_address),
        "Lines per address": get_stats(lines_per_address),
        "Assembly Lines per addr": get_stats(assembly_lines_per_address),
        "Contracts per address": get_stats(contracts_per_address),
        "Funcs per address": get_stats(functions_per_address),
        "Funcs with assembly per addr": get_stats(functions_with_assembly_per_address),
        "Fragments per address": get_stats(fragments_per_address),
    }
    title = "General statistics of addresses with inline assembly"
    print_res(title, general_stats, 'table')


def print_rq_question(question):
    lenght = len(question)
    print(question)
    print(lenght * '-')
    print()


def rq6(con, limit=30):
    question = ("What percentage of inline assembly should a tool support to "
                "handle 80% of smart contracts with inline assembly?")
    print_rq_question(question)
    total_addresses = process_res(
        run_query(con, QUERIES['total_addresses']), 'value'
    )

    top_opcodes_query = QUERIES['top_x'].format(
         id='opcode_id',
         per_frag='OpcodesPerFragment',
         aggr='COUNT',
         limit=30
    )
    top_opcodes = process_res(
        run_query(con, top_opcodes_query), 'values'
    )

    all_but_top_10_opcodes = [str(v) for v in OPCODES.values()
                              if v not in top_opcodes]
    high_level_constructs = [str(v) for v in HIGH_LEVEL_CONSTRUCTS.values()]
    old_opcodes = [str(v) for v in OLD_OPCODES.values()]
    declarations = [str(v) for k, v in DECLARATIONS.items() if k != 'let']

    containing_query = QUERIES['addresses_containing'].format(
        opcodes=",".join(all_but_top_10_opcodes),
        declarations=",".join(declarations),
        old_opcodes=",".join(old_opcodes),
        high_level_constructs=",".join(high_level_constructs)
    )
    containing_res = process_res(
        run_query(con, containing_query), 'values'
    )
    res = 1 - (len(containing_res) / total_addresses)
    s = ("By implement the {} most popular OPCODES and simply declarations: "
         "{:.2f} of total addresses can be handled.").format(limit, res)
    print(s)


def get_latex(name, value, symbol='', use_num=True):
    if isinstance(value, float):
        value = "{:.2f}".format(value)
    if use_num:
        return f"\\newcommand{{\\{name}}}{{\\num{{{value}}}{symbol}\\xspace}}"
    return f"\\newcommand{{\\{name}}}{{${value}${symbol}\\xspace}}"


def print_latex(name, value, symbol='', use_num=True):
    print(get_latex(name, value, symbol, use_num=use_num))


def get_total_instructions_per(con, filters={}):
    addresses = defaultdict(lambda: 0)
    fragments = defaultdict(lambda: 0)
    per_unique_fragments = defaultdict(lambda: 0)
    for instr, values in INSTRUCTIONS.items():
        table_name_per, table_name = values
        instr_in_addresses = process_res(
            run_query(
                con, 'instructions_in_addresses_per_address',
                {'instr':instr, 'table_per':table_name_per,
                 'table':table_name},
                filters=filters
            ), 'tuples')
        instr_in_fragments = process_res(
            run_query(
                con, 'instructions_per_fragment',
                {'instr':instr, 'table_per':table_name_per,
                 'table':table_name},
                filters=filters
            ), 'tuples')
        instr_in_unique_fragments = process_res(
            run_query(
                con, 'instructions_per_unique_fragment',
                {'instr':instr, 'table_per':table_name_per,
                 'table':table_name},
                filters=filters
            ), 'tuples')
        for addr, instr in instr_in_addresses:
            addresses[addr] += instr
        for frag, instr in instr_in_fragments:
            fragments[frag] += instr
        for uniq_frag, instr in instr_in_unique_fragments:
            per_unique_fragments[uniq_frag] += instr
    return ([v for v in addresses.values()], [v for v in fragments.values()],
            [v for v in per_unique_fragments.values()])


def get_cumulative_distribution(values):
    """Gets list of values and returns sorted list of values and percentages.
    """
    x_dict = defaultdict(lambda: 0)
    for v in values:
        x_dict[v] += 1
    total = len(values)  # number of X
    number_of_v = sorted(x_dict.keys())
    number_of_occurences = [x_dict[k] for k in number_of_v]
    percentages = [(sum(number_of_occurences[:i]) / total) * 100
                   for i in range(1, len(number_of_occurences)+1)]
    return number_of_v, percentages


def measuring(con, figures, latex=False, disable_figures=False, filters={}):
    def compute_addresses():
        assembly_contract_perc = get_perc(assembly_addresses, total_addresses)
        assembly_contract_unique_perc = get_perc(
            assembly_addresses_unique, total_addresses_unique)
        return assembly_contract_perc, assembly_contract_unique_perc

    def density():
        print("--Density of inline assembly fragments--")
        total_locs = sum(process_res(
            run_query(con, 'lines_per_address', filters=filters), 'values'
        ))
        one_frag_per_x_locs = int(total_locs / total_fragments)
        print(f"One fragment per {one_frag_per_x_locs} LOCS")
        print("----------------------------------------")
        return one_frag_per_x_locs

    def fragments():
        fragments_per_address_stats = get_stats(fragments_per_address)
        fragments_per_unique_address_stats = get_stats(fragments_per_unique_address)
        if not disable_figures:
            #fragments_hist_figure = os.path.join(figures, 'fragments_hist.pdf')
            #print(f"Saving histogram at {fragments_hist_figure}")
            #plot_histogram_tweaked(fragments_hist_figure, fragments_per_address,
            #                       10, 20, 1, 5, "Inline Assembly Fragments",
            #                       "Contract Addresses")
            # Cumulative
            fragments_cum_figure = os.path.join(figures, 'fragments_cum.pdf')
            print(f"Saving cumulative distribution at {fragments_cum_figure}")
            (number_of_fragments,
             fragments_percentage) = get_cumulative_distribution(
                     fragments_per_address)
            plot_signle_line(fragments_cum_figure,
                             number_of_fragments,
                             fragments_percentage,
                             "Number of fragments",
                             "Percentage",
                             [1, 10, 20, 30, 40, 50, 60, 70, 81]
                             ,"blue")
        return fragments_per_address_stats, fragments_per_unique_address_stats

    def unique_fragments():
        unique_fragments = process_res(
            run_query(con, 'unique_fragments', filters=filters), 'value'
        )
        uf_perc = get_perc(unique_fragments, total_fragments)
        print(f"{unique_fragments}/{total_fragments} ({uf_perc}%) fragments are unique")
        unique_fragments_per_address = get_stats(process_res(
            run_query(con, 'unique_fragments_per_address', filters=filters),
            'values'
        ))
        unique_fragments_per_address_table = {
            'Unique Fragments': unique_fragments_per_address}
        return unique_fragments, uf_perc, unique_fragments_per_address

    def instructions():
        instructions_per_fragment_stats = get_stats(
            total_instructions_per_fragment)
        instructions_per_unique_fragment_stats = get_stats(
            total_instructions_per_unique_fragment)
        # Histogram
        if not disable_figures:
            instructions_hist_figure = os.path.join(figures,
                                                    'instructions_hist.pdf')
            print(f"Saving histogram at {instructions_hist_figure}")
            plot_histogram_tweaked(instructions_hist_figure,
                                   total_instructions_per_unique_fragment,
                                   20, 50, 1, 10, "Instructions",
                                   "Fragments", xticks_font=16)
        # Cumulative
        #instructions_cum_figure = os.path.join(figures, 'instructions_cum.pdf')
        #print(f"Saving cumulative distribution at {instructions_cum_figure}")
        #(number_of_instructions,
        # fragments_instr_percentage) = get_cumulative_distribution(
        #         total_instructions_per_fragment)
        #plot_signle_line(instructions_cum_figure,
        #                 number_of_instructions,
        #                 fragments_instr_percentage,
        #                 "Number of Instructions",
        #                 "Percentage",
        #                 [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110]
        #                 ,"blue")
        return (instructions_per_fragment_stats,
                instructions_per_unique_fragment_stats)

    title = "RQ1: Measuring Inline Assembly"
    print_rq_question(title)

    # Data that we are using throught the function
    fragments_per_address = process_res(
        run_query(con, 'fragments_per_address', filters=filters), 'values'
    )
    fragments_per_unique_address = process_res(
        run_query(con, 'fragments_per_unique_address', filters=filters),
        'values'
    )
    (total_instructions_per_address,
     total_instructions_per_fragment,
     total_instructions_per_unique_fragment) = get_total_instructions_per(
             con, filters=filters)
    total_fragments = sum(fragments_per_address)
    without_addresses, assembly_addresses, total_addresses = get_addresses(
            con, filters)
    (without_addresses_unique,
     assembly_addresses_unique,
     total_addresses_unique) = get_unique_addresses(con, filters)

    assembly_contract_perc, assembly_contract_unique_perc = compute_addresses()
    print()
    one_frag_per_x_locs = density()
    print()
    fragments_per_address_stats, fragments_per_unique_address_stats = fragments()
    print()
    unique_fragments, uf_perc, unique_fragments_per_address = unique_fragments()
    print()
    (instructions_per_fragment_stats,
     instructions_per_unique_fragment_stats) = instructions()
    print()

    statistics_table = {
            "Total Contracts": {"Total": total_addresses},
            "Total Contracts using Inline Assembly": {
                "Total": f"{assembly_addresses} ({assembly_contract_perc}%)"},
            "Total Unique Contracts": {"Total": total_addresses_unique},
            "Total Unique Contracts using Inline Assembly": {
                "Total": f"{assembly_addresses_unique} ({assembly_contract_unique_perc}%)"},
            "Total Inline Assembly Fragments": {"Total":
                fragments_per_address_stats['total']},
            "Total Inline Assembly Fragments in Unique Addresses": {"Total":
                fragments_per_unique_address_stats['total']},
            "Total Inline Assembly Unique Fragments": {"Total":
                unique_fragments},
            "Total Instructions": {"Total":
                instructions_per_fragment_stats['total']}
    }
    print_res('Statistics Table', statistics_table, 'table', first_col=55)

    frag_instr_table = {
        "Fragments per contract": fragments_per_address_stats,
        "Unique fragments per contract":  unique_fragments_per_address,
        "Instructions per fragment": instructions_per_fragment_stats,
        "Instructions per unique fragment": instructions_per_unique_fragment_stats
    }
    print_res('Fragments and Instructions Table', frag_instr_table,
              'table', first_col=40)

    if latex:
        print(":::::LATEX:::::")
        print("% Addresses")
        print_latex("totaladdresses", total_addresses)
        print_latex("addresseswith", assembly_addresses)
        print_latex("addresseswithperc", assembly_contract_perc, "\\%")
        print_latex("totaladdressesunique", total_addresses_unique)
        print_latex("addresseswithunique", assembly_addresses_unique)
        print_latex("addresseswithpercunique", assembly_contract_unique_perc, "\\%")
        print_latex("addresseswithout", without_addresses)
        print("% Density")
        print_latex("fragmentperlocs", one_frag_per_x_locs)
        print("% Fragments")
        print_latex("totalfragments", fragments_per_address_stats['total'])
        print_latex("totalfragmentsuniqueaddresses",
                    fragments_per_unique_address_stats['total'])
        print_latex("maxfragmentsperaddress",
                    fragments_per_address_stats['max'])
        print_latex("minfragmentsperaddress",
                    fragments_per_address_stats['min'])
        print_latex("meanfragmentsperaddress",
                    fragments_per_address_stats['mean'])
        print_latex("medianfragmentsperaddress",
                    fragments_per_address_stats['median'])
        print_latex("sdfragmentsperaddress",
                    fragments_per_address_stats['sd'])
        print("% Unique")
        print_latex("uniquefragments", unique_fragments)
        print_latex("uniquefragmentsperc", uf_perc, '\\%')
        print_latex("maxuniquefragmentsperaddress",
                    unique_fragments_per_address['max'])
        print_latex("minuniquefragmentsperaddress",
                    unique_fragments_per_address['min'])
        print_latex("meanuniquefragmentsperaddress",
                    unique_fragments_per_address['mean'])
        print_latex("medianuniquefragmentsperaddress",
                    unique_fragments_per_address['median'])
        print_latex("sduniquefragmentsperaddress",
                    unique_fragments_per_address['sd'])
        print("% Instructions")
        print_latex("totalinstructions",
                    instructions_per_fragment_stats['total'])
        print_latex("totalinstructionsuniquefragments",
                    instructions_per_unique_fragment_stats['total'])
        print_latex("maxinstructionsperfragment",
                    instructions_per_fragment_stats['max'])
        print_latex("mininstructionsperfragment",
                    instructions_per_fragment_stats['min'])
        print_latex("meaninstructionsperfragment",
                    instructions_per_fragment_stats['mean'])
        print_latex("medianinstructionsperfragment",
                    instructions_per_fragment_stats['median'])
        print_latex("sdinstructionssperfragment",
                    instructions_per_fragment_stats['sd'])
        print_latex("maxinstructionsperuniquefragment",
                    instructions_per_unique_fragment_stats['max'])
        print_latex("mininstructionsperuniquefragment",
                    instructions_per_unique_fragment_stats['min'])
        print_latex("meaninstructionsperuniquefragment",
                    instructions_per_unique_fragment_stats['mean'])
        print_latex("medianinstructionsperuniquefragment",
                    instructions_per_unique_fragment_stats['median'])
        print_latex("sdinstructionssperuniquefragment",
                    instructions_per_unique_fragment_stats['sd'])
        print(":::::::::::::::")


def smart_contract_characteristics(con, figures, latex, disable_figures, filters):
    title = "RQ2: Smart Contract Characteristics"
    print_rq_question(title)

    without_addresses, assembly_addresses, total_addresses = get_addresses(
            con, filters)
    attributes = ['nr_transactions', 'unique_callers', 'nr_token_transfers',
                  'is_erc20', 'is_erc721', 'tvl', 'loc']
    def process_characteristics(address_category, query):
        attributes_res = {}
        for attribute in attributes:
            attributes_res[attribute] = {
                'counts': defaultdict(lambda: 0), 'list': [], 'stats': None}

        characteristics = process_res(
            run_query(con, query, filters=filters), 'tuples'
        )

        for row in characteristics:
            for attribute, value in zip(attributes, row):
                attributes_res[attribute]['counts'][value] += 1
                attributes_res[attribute]['list'].append(value)
        for attribute in attributes:
            if attribute in ('is_erc721', 'is_erc20'):
                continue
            attributes_res[attribute]['stats'] = get_stats(
                    attributes_res[attribute]['list']
            )
        return attributes_res

    assembly_res = process_characteristics("Assembly",
                                           "addresses_characteristics")
    non_assembly_res = process_characteristics(
            "Non Assembly", 'non_assembly_addresses_characteristics')

    res = {}
    lookup_names = {
        'nr_transactions' : 'Transactions',
        'unique_callers': 'Unique Callers',
        'nr_token_transfers': 'Token Transfers',
        'tvl': 'TVL',
        'loc': 'LOC'
    }
    for attribute in attributes:
        if attribute in ('is_erc721', 'is_erc20'):
            continue

        res['Non Assembly ' + attribute] = non_assembly_res[attribute]['stats']
        res['Assembly ' + attribute] = assembly_res[attribute]['stats']

        if not disable_figures:
            if attribute in ('tvl', 'loc'):
                continue
            name = 'comp_' + attribute + '.pdf'
            fig = os.path.join(figures, name)
            print(f"Saving {fig}")
            # loc may be empty if we haven't provided them.
            assembly_res[attribute]['list'] = list(filter(
                lambda x: x != '', assembly_res[attribute]['list']))
            non_assembly_res[attribute]['list'] = list(filter(
                lambda x: x != '', non_assembly_res[attribute]['list']))
            plot_histogram_tweaked(
                fig, assembly_res[attribute]['list'],
                10, 30, 1, 10,
                "Number of " + lookup_names[attribute],
                "Percentage of contract addresses",
                perc=True,
                start_pos=0,
                extra_dataset=(non_assembly_res[attribute]['list'],),
                legend=['Assembly', 'Non Assembly'])
    print()

    print_res("Characteristics", res, 'table', first_col=36)

    def get_fragment_stats_for_contracts_with_specific_chars(args):
        fragments_table = {}
        for char, comp, value in args:
            fragments_per_address = process_res(run_query(
                con, 'fragments_per_address_filter',
                {'char': char, 'comp': comp, 'value': value}, filters
            ), 'values')
            if len(fragments_per_address) == 0:
                print(f"No results found for: '{char} {comp} {value}'")
                continue
            fragments_per_address_stats = get_stats(fragments_per_address)
            row_name = "When {} {} {}".format(char, comp, value)
            fragments_table[row_name] = fragments_per_address_stats
        print_res('Fragments', fragments_table, 'table')

    get_fragment_stats_for_contracts_with_specific_chars(
        [("a.nr_transactions", ">", 50000), ("a.nr_transactions", "<=", 50000)]
    )

    print()
    def get_erc_perc(res, erc, total, precision):
        total_erc = sum(1 for i in res[erc]['list'] if i == 'true')
        return get_perc(total_erc, total, precision=precision)
    non_assembly_erc20_perc = get_erc_perc(non_assembly_res, 'is_erc20',
                                           without_addresses, precision=2)
    non_assembly_erc721_perc = get_erc_perc(non_assembly_res, 'is_erc721',
                                            without_addresses, precision=2)
    assembly_erc20_perc = get_erc_perc(assembly_res, 'is_erc20',
                                       without_addresses, precision=2)
    assembly_erc721_perc = get_erc_perc(assembly_res, 'is_erc721',
                                        without_addresses, precision=2)

    print("----------ERC20 and ERC721----------")
    print(f"Non Assembly ERC20 percentage: {non_assembly_erc20_perc}%")
    print(f"Assembly ERC20 percentage: {assembly_erc20_perc}%")
    print(f"Non Assembly ERC721 percentage: {non_assembly_erc721_perc}%")
    print(f"Assembly ERC721 percentage: {assembly_erc721_perc}%")
    print("------------------------------------")

    print()
    def most_common_labels(table, limit):
        labels = process_res(run_query(
            con, 'top_labels', {'table': table}
        ), 'tuples' )[:limit]
        labels = convert_tuples_to_dict(labels)
        res = {l: {"Addresses": v[0]} for l, v in labels.items()}
        print_res(f"Top {limit} {table} labels", res, 'table', first_col=24)
        return res
    # Labels
    #assembly_top_labels = most_common_labels('Address', 50)
    #non_assembly_top_labels = most_common_labels('NonAssemblyAddress', 50)
    #def get_biggest_differences(a, b):
    #    in_a_labels = {
    #        l: v["Addresses"] - b.get(l, {"Addresses": 0})["Addresses"]
    #        for l, v in a.items()}
    #    return dict(sorted(in_a_labels.items(), key=lambda item: item[1]))
    #print("With differences top {50}")
    #print(get_biggest_differences(assembly_top_labels, non_assembly_top_labels))
    #print("Without differences top {50}")
    #print(get_biggest_differences(non_assembly_top_labels, assembly_top_labels))


    if latex:
        print(":::::LATEX:::::")
        print("% Stats")
        for attribute in attributes:
            if attribute in ('is_erc721', 'is_erc20'):
                continue
            for t, value in non_assembly_res[attribute]['stats'].items():
                name = f"nonassembly{attribute}{t}".replace('_', '')
                print_latex(name, value)
            for t, value in assembly_res[attribute]['stats'].items():
                name = f"assembly{attribute}{t}".replace('_', '')
                print_latex(name, value)
        print("% ERC")
        print_latex("nonassemblyercperc", non_assembly_erc20_perc, "\\%")
        print_latex("assemblyercperc", assembly_erc20_perc, "\\%")
        print_latex("nonassemblynftperc", non_assembly_erc721_perc, "\\%")
        print_latex("assemblynftperc", assembly_erc721_perc, "\\%")
        print(":::::::::::::::")


def evolution(con, figures, latex, disable_figures, filters):
    title = "RQ3: Evolution of Inline Assembly"
    print_rq_question(title)

    # Blocks
    if not disable_figures:
        figure = os.path.join(figures, 'evolution_blocks.pdf')
        assembly_block = convert_tuples_to_dict(process_res(
            run_query(con, 'blocks_assembly', filters=filters), 'tuples'
        ))
        non_assembly_block = convert_tuples_to_dict(process_res(
            run_query(con, 'blocks_non_assembly', filters=filters), 'tuples'
        ))
        all_blocks = {block: {'assembly': assembly_block.get(block, [0])[0],
                              'non_assembly': non_assembly[0]}
                      for block, non_assembly in non_assembly_block.items()}
        for block, assembly in assembly_block.items():
            if block not in all_blocks:
                all_blocks[block] = {'assembly': assembly[0], 'non_assembly': 0}
        all_blocks.pop('', None)
        blocks = sorted(all_blocks, key=lambda x: int(x))
        count_assembly = 0
        count_non_assembly = 0
        percentages = []
        only_non_assembly = []
        only_assembly = []
        for block in blocks:
            count_assembly += all_blocks[block]['assembly']
            count_non_assembly += all_blocks[block]['non_assembly']
            count_total = count_assembly + count_non_assembly
            percentages.append(count_assembly/count_total)
            only_assembly.append(count_assembly)
            only_non_assembly.append(count_total)
        print(f"Saving result to {figure}")
        plot_signle_line(
            figure, blocks, percentages,
            'Date',
            '\\% of contracts using assembly',
            [blocks[0], 2025000, 4130000, 6105000,
             8305000, 10610000, 12575000, blocks[-1]],
            xticks_labels=['2015', '2016', '2017', '2018', '2019', '2020',
                           '2021', '2022'],
            color='blue',
            secondary_data=only_non_assembly,
            yticks_secondary=[0, 500000, 1000000, 1500000, 2000000, 2500000,
                              3000000, 3500000, 4000000, 4500000, 5000000,
                              5500000, 6000000, 6500000, 7000000, 7500000],
            ylabel_secondary='Number of Contracts',
            second_label='Number of contracts without assembly',
            third_data=only_assembly,
            third_label='Number of contracts with assembly',
            legend=True
            )

    # Compiler versions
    def get_per_major_version(query):
        resultset= process_res(
            run_query(con, query, filters=filters), 'values'
        )
        res = defaultdict(lambda: 0)
        count_empty_versions = 0
        for version in resultset:
            if version == '':
                count_empty_versions += 1
                continue
            _, major, _ = get_compiler_version(version).split('.')[:3]
            res[major] += 1
        #print(f"Empty version: {count_empty_versions}")
        return res
    print()
    assembly_compiler = get_per_major_version('compiler_assembly')
    non_assembly_compiler = get_per_major_version('compiler_non_assembly')
    res = {v: {'non assembly': non_assembly_compiler.get(v, 0),
               'assembly': assembly_compiler.get(v, 0),
               'perc': get_perc(assembly_compiler.get(v, 0),
               (assembly_compiler.get(v, 0) + non_assembly_compiler.get(v, 0)))}
           for v in non_assembly_compiler}
    res = dict(sorted(res.items(), key=lambda item: item[0]))
    print_res("Percentages per compiler version", res, 'table', first_col=5)

    if latex:
        print("% Compiler versions")
        numbers = ['one', 'two', 'three', 'four', 'five', 'six', 'seven',
                   'eight']
        for major, name in zip(res, numbers):
            print_latex(f"compiler{name}nonassembly", res[major]['non assembly'])
            print_latex(f"compiler{name}assembly", res[major]['assembly'])
            print_latex(f"compiler{name}perc", res[major]['perc'], "\\%")
        print(":::::::::::::::")


def taxonomy(con, figures, latex, disable_figures, filters):
    def sort_dict(d):
        return dict(sorted(
            d.items(),
            key=lambda item: item[1]['perc'],
            reverse=True
        ))

    def process_category(name, category):
        print(f"### {name} ###")
        latex_commands.append(f"% {name}")
        print()
        opcodes = []
        high_level_constructs = []
        old_opcodes = []
        declarations = []
        for subcategory, values in category.items():
            subcategory_dict = {
                v: instructions_data.get(v, {'perc': 0, 'occ': 0, 'total': 0})
                for v in values
            }
            for instr, r in subcategory_dict.items():
                for k, v in r.items():
                    latex_commands.append(
                        get_latex(instr + k, v, "\\%" if k == 'perc' else '')
                    )
            subcategory_dict = sort_dict(subcategory_dict)
            print_res(subcategory, subcategory_dict, 'table', first_col=20)
            for v in values:
                if v in OPCODES:
                    opcodes.append(str(OPCODES[v]))
                elif v in HIGH_LEVEL_CONSTRUCTS:
                    high_level_constructs.append(str(HIGH_LEVEL_CONSTRUCTS[v]))
                elif v in OLD_OPCODES:
                    old_opcodes.append(str(OLD_OPCODES[v]))
                elif v in DECLARATIONS:
                    declarations.append(str(DECLARATIONS[v]))
        print()
        containing_query_params = {
                'opcodes': ",".join(opcodes),
                'declarations': ",".join(declarations),
                'old_opcodes': ",".join(old_opcodes),
                'high_level_constructs': ",".join(high_level_constructs)
        }
        containing_res = process_res(
            run_query(con, 'addresses_containing',
                      containing_query_params, filters=filters), 'values'
        )
        res = get_perc(len(containing_res), assembly_addresses, 4)
        print("####{}####".format(len(name) * "#"))
        category_percentages[name] = {'perc': res}
        category_addresses[name] = set(containing_res)
        category_cmd_name = name.replace(' ', '').lower() + 'perc'
        latex_commands.append(
            get_latex(category_cmd_name, res, "\\%")
        )
        print()

    title = "RQ4: A Taxonomy of Inline Assembly"
    print_rq_question(title)

    assembly_addresses = process_res(
        run_query(con, 'total_addresses', filters=filters), 'value'
    )

    latex_commands = []

    instructions_data = {}
    for instr, values in INSTRUCTIONS.items():
        table_name_per, table_name = values
        instr_in_addresses = process_res(run_query(
            con, 'instructions_in_addresses',
            {'instr': instr, 'table_per': table_name_per, 'table': table_name},
            filters=filters
        ), 'tuples')
        instr_in_addresses = [t[1:] for t in instr_in_addresses]
        instr_in_addresses = convert_tuples_to_dict(instr_in_addresses)
        instr_in_addresses = get_stats_instr(assembly_addresses, instr_in_addresses)
        instructions_data.update(instr_in_addresses)

    category_percentages = {}
    category_addresses = {}
    categories = [
        ("Arithmetic Operations", ARITHMETIC_OPERATIONS),
        ("Comparison and Bitwise Logic Operations", COMPARISON_BITWISE),
        ("Hashing Operations", HASH_OPERATIONS),
        ("Enviromental Information", ENVIROMENTAL_INFORMATION),
        ("Block Information", BLOCK_INFORMATION),
        ("Stack, Memory, and Storage Operations", STACK_MEMORY_STORAGE),
        ("Flow Operations", FLOW_OPERATIONS),
        ("System Operations", SYSTEM_OPERATIONS),
        ("YUL Declarations", YUL_DECLARATIONS),
        ("Push, Duplication, and Exchange Operations", PUSH_DUP_SWAP),
        ("Logging Operations", LOGGING_OPERATIONS),
        ("YUL Special Instructions", YUL_SPECIAL_INSTRUCTIONS),
    ]
    for name, category in categories:
        process_category(name, category)
    category_percentages = sort_dict(category_percentages)
    print_res("Instruction groups", category_percentages,
              'table', first_col=45)

    if not disable_figures:
        all_addr_values = {i for v in category_addresses.values() for i in v}
        categories_df = pd.DataFrame()
        column_names = []
        for category, addresses in category_addresses.items():
            if len(addresses) < 0.01 * len(all_addr_values):
                continue
            if len(category) > 30:
                category = category.replace('Operations', '')
            column_names.append(category)
            temp = []
            for addr in all_addr_values:
                if addr in addresses:
                    temp.append(True)
                else:
                    temp.append(False)
            categories_df[category] = temp
        categories_df['c'] = 1
        categoriesplot_df = categories_df.groupby(
            column_names).count().sort_values('c')
        figure = os.path.join(figures, 'taxonomy_categories.pdf')
        try:
            useplot(figure, categoriesplot_df['c'], sort_by='cardinality',
                    min_subset_size=500, show_percentages=False)
        except:
            print(f"Could not generate {figure}")

    if latex:
        for c in latex_commands:
            c = c.replace('log0', 'logzero')
            c = c.replace('log1', 'logone')
            c = c.replace('log2', 'logtwo')
            c = c.replace('log3', 'logthree')
            c = c.replace('log4', 'logfour')
            c = c.replace('keccak256', 'keccak')
            c = c.replace('sha3', 'sha')
            c = c.replace('mstore8', 'mstoreeight')
            c = c.replace('stack,memory,andstorageoperationsperc',
                          'stackmemoryandstorageoperationsperc')
            c = c.replace('create2', 'createtwo')
            c = c.replace('push,duplication,andexchangeoperationsperc',
                          'pushduplicationandexchangeoperationsperc')
            print(c)


def print_sections(con, figures, latex, disable_figures, filters):
    print()
    measuring(con, figures, latex, disable_figures, filters)
    print()
    smart_contract_characteristics(con, figures, latex, disable_figures, filters)
    print()
    evolution(con, figures, latex, disable_figures, filters)
    print()
    taxonomy(con, figures, latex, disable_figures, filters)


def select_fragments(con, output_filename):
    lines = []
    hashes = set()

    def get_top(query_name, part, start_number, end_number,
                extra=None, extra2=None):
        print(f"Process {part}")
        lines.append(part.center(80, '#'))
        query = QUERIES[query_name].format(end_number)
        res = process_res(run_query(con, query), 'tuples')
        counter = start_number
        for r in res:
            (fragment_hash, total, code, start_line, end_line, contract_name,
             file_name, address, solidity_version_etherscan, block_number,
             extra_value, extra_value2) = r
            if fragment_hash in hashes:
                continue
            hashes.add(fragment_hash)
            lines.append('metadata'.center(40, ':'))
            lines.append(f'Number                    {counter}')
            lines.append(f'Hash                      {fragment_hash}')
            lines.append(f'Total                     {total}')
            if extra:
                spaces = len('                          ') - len(extra)
                spaces = spaces * ' '
                lines.append(f'{extra}{spaces}{extra_value}')
            if extra2:
                spaces = len('                          ') - len(extra2)
                spaces = spaces * ' '
                lines.append(f'{extra2}{spaces}{extra_value2}')
            lines.append(f'Address                   {address}')
            lines.append(f'Solidity Version          {solidity_version_etherscan}')
            lines.append(f'Block Number              {block_number}')
            lines.append(f'Filename                  {file_name}')
            lines.append(f'Contract Name             {contract_name}')
            lines.append(f'Start Line                {start_line}')
            lines.append(f'End Line                  {end_line}')
            lines.append(40*':')
            lines.append('analysis'.center(40, '+'))
            lines.append('Comments')
            lines.append('Identical')
            lines.append('Similar')
            lines.append('Category')
            lines.append(40*'+')
            lines.append('code'.center(40, '-'))
            lines.append(code)
            lines.append(40*'-')
            counter += 1
            if counter > end_number:
                break
        lines.append(80*'#')

    unique_fragments = process_res(
        run_query(con, QUERIES['unique_fragments']), 'value'
    )
    total_fragments = process_res(
        run_query(con, QUERIES['total_fragments']), 'value'
    )
    # Get 20 more from each category to filter out identical fragments
    padding = 20
    first, last = 1, 50 + padding
    get_top('top_fragments',
            'Top fragments by occurences', first, last)
    query = QUERIES['total_fragments_in'].format(
                ",".join(f'"{h}"' for h in hashes))
    top_fragments_percentage = get_perc(process_res(
        run_query(con, query), 'value'),
        total_fragments)
    first, last = 51 + padding, 70 + 2*padding
    get_top('top_fragments_transactions',
            'Top fragments by number of transactions',
            first, last, 'Transactions Number')
    first, last = 71 + 2*padding, 90 + 3*padding
    get_top('top_fragments_unique_callers',
            'Top fragments by unique callers',
            first, last, 'Unique callers')
    first, last = 91 + 3*padding, 110 + 4*padding
    get_top('top_fragments_contracts',
            'Top fragments by unique contracts',
            first, last, 'Address Duplicates', 'Address Hash')
    first, last = 111 + 4*padding, 130 + 5*padding
    get_top('random_fragments',
            'Random fragments',
            first, last)
    with open(output_filename, 'w') as f:
        for line in lines:
            f.write(line + '\n')
    print(f'Unique fragments: {unique_fragments}')
    print(f'Total fragments: {total_fragments}')
    print(f'Percentage of top 70: {top_fragments_percentage}%')


def get_args():
    parser = argparse.ArgumentParser(
        description='Query the database.')
    parser.add_argument(
        "db", help="Database"
    )
    parser.add_argument(
        "-t", "--total-contracts",
        type=int,
        help="Pass the number of total contracts, print sources info."
    )
    parser.add_argument(
        "-s", "--print-statistics",
        action='store_true',
        help="Print general statistics."
    )
    parser.add_argument(
        "-Q", "--quantitative-analysis",
        action='store_true',
        help="Perform quantitative analysis"
    )
    parser.add_argument(
        "-1", "--rq1",
        action='store_true',
        help="Compute and print the results for RQ1"
    )
    parser.add_argument(
        "-2", "--rq2",
        action='store_true',
        help="Compute and print the results for RQ2"
    )
    parser.add_argument(
        "-3", "--rq3",
        action='store_true',
        help="Compute and print the results for RQ3"
    )
    parser.add_argument(
        "-4", "--rq4",
        action='store_true',
        help="Compute and print the results for RQ4"
    )
    parser.add_argument(
        "-l", "--latex",
        action='store_true',
        help="Print latex commands"
    )
    parser.add_argument(
        "-f", "--figures",
        default='figures',
        help="Directory to save figures"
    )
    parser.add_argument(
        "--tx-value",
        type=int,
        help="Number of transactions to use for filtering"
    ),
    parser.add_argument(
        "--tx-cond",
        choices=[">", ">=", "<", "<=", "="],
        help="Condition to use when filtering with number of transactions"
    ),
    parser.add_argument(
        "--tk-value",
        type=int,
        help="Number of token transfers to use for filtering"
    ),
    parser.add_argument(
        "--tk-cond",
        choices=[">", ">=", "<", "<=", "="],
        help="Condition to use when filtering with number of token transfers"
    ),
    parser.add_argument(
        "--filters-conditional",
        choices=["AND", "OR"],
        default="AND",
        help="Select AND or OR when using both --tk-value and --tx-value (Default: AND)"
    ),
    parser.add_argument(
        "--disable-figures",
        action='store_true',
        help="Do not create figures"
    )
    parser.add_argument(
        "--select-qualitative",
        help="Select fragments for the qualitative analysis and save them to file"
    )
    args = parser.parse_args()
    if args.tx_value is not None and args.tx_cond is None:
        sys.exit("You cannot use --tx-cond without --tx-value and vice versa.")
    if args.tx_cond is not None and args.tx_value is None:
        sys.exit("You cannot use --tx-cond without --tx-value and vice versa.")
    if args.tk_value is not None and args.tk_cond is None:
        sys.exit("You cannot use --tk-cond without --tk-value and vice versa.")
    if args.tk_cond is not None and args.tk_value is None:
        sys.exit("You cannot use --tk-cond without --tk-value and vice versa.")
    return args


def main():
    args = get_args()
    filters = {}
    if args.tx_value or args.tk_value:
        filters = {
             "comp_tx": ">=",
             "nr_tx": "0",
             "comp_tk": ">=",
             "nr_tk": "0",
             "filters_cond": args.filters_conditional
        }
        if args.tx_value:
            filters['comp_tx'] = args.tx_cond
            filters['nr_tx'] = args.tx_value
        if args.tk_value:
            filters['comp_tk'] = args.tk_cond
            filters['nr_tk'] = args.tk_value
    con = connect(args.db)
    if args.total_contracts:
        print_sources_statistics(con, args.total_contracts, args.latex, filters)
    if args.select_qualitative:
        select_fragments(con, args.select_qualitative)
    if args.print_statistics:
        print_statistics(con, filters)
    if args.quantitative_analysis:
        create_dirs(args.figures)
        print("Sections")
        print("========")
        print_sections(con, args.figures, args.latex, args.disable_figures,
                       filters)
    if args.rq1:
        measuring(con, args.figures, args.latex, args.disable_figures, filters)
    if args.rq2:
        smart_contract_characteristics(con, args.figures, args.latex,
            args.disable_figures, filters)
    if args.rq3:
        evolution(con, args.figures, args.latex, args.disable_figures, filters)
    if args.rq4:
        taxonomy(con, args.figures, args.latex, args.disable_figures, filters)
    con.close()


if __name__ == "__main__":
    main()
