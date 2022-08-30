"""
Queries templates for inline.db
"""
QUERIES = {
    "non_inline_addresses": "SELECT COUNT(*) FROM NonAssemblyAddress",
    "non_inline_addresses_filtered": (
        "SELECT COUNT(*) FROM NonAssemblyAddress "
        "WHERE nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} nr_token_transfers {comp_tk} {nr_tk}"
    ),

    "total_addresses": "SELECT COUNT(*) FROM Address",
    "total_addresses_filtered": (
        "SELECT COUNT(*) FROM Address "
        "WHERE nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} nr_token_transfers {comp_tk} {nr_tk}"
    ),

    "non_inline_addresses_unique": (
        "SELECT COUNT(DISTINCT hash) "
        "FROM NonAssemblyAddress"
    ),
    "non_inline_addresses_unique_filtered": (
        "SELECT COUNT(DISTINCT hash) "
        "FROM NonAssemblyAddress "
        "WHERE nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} nr_token_transfers {comp_tk} {nr_tk}"
    ),

    "total_addresses_unique": (
        "SELECT COUNT(DISTINCT hash) "
        "FROM Address"
    ),
    "total_addresses_unique_filtered": (
        "SELECT COUNT(DISTINCT hash) "
        "FROM Address "
        "WHERE nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} nr_token_transfers {comp_tk} {nr_tk}"
    ),

    "files_per_address": "SELECT COUNT(*) FROM SolidityFile GROUP BY address_id",
    "files_per_address_filtered": (
        "SELECT COUNT(*) FROM SolidityFile AS s "
        "JOIN Address AS a ON a.address_id = s.address_id "
        "WHERE a.nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} a.nr_token_transfers {comp_tk} {nr_tk} "
        "GROUP BY s.address_id"
    ),

    "lines_per_address": "SELECT SUM(lines) FROM SolidityFile GROUP BY address_id",
    "lines_per_address_filtered": (
        "SELECT SUM(lines) FROM SolidityFile AS s "
        "JOIN Address as a ON a.address_id = s.address_id "
        "WHERE a.nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} a.nr_token_transfers {comp_tk} {nr_tk} "
        "GROUP BY s.address_id"
     ),

    "functions_per_address": (
        "SELECT SUM(funcs) "
        "FROM Contract AS c "
        "JOIN SolidityFile as S ON c.file_id = s.file_id "
        "GROUP BY s.address_id"
    ),
    "functions_per_address_filtered": (
        "SELECT SUM(funcs) "
        "FROM Contract AS c "
        "JOIN SolidityFile as S ON c.file_id = s.file_id "
        "JOIN Address as a ON a.address_id = s.address_id "
        "WHERE a.nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} a.nr_token_transfers {comp_tk} {nr_tk} "
        "GROUP BY s.address_id"
    ),

    "functions_with_assembly_per_address": (
        "SELECT SUM(funcs_with_assembly) "
        "FROM Contract AS c "
        "JOIN SolidityFile as S ON c.file_id = s.file_id "
        "GROUP BY s.address_id"
    ),
    "functions_with_assembly_per_address_filtered": (
        "SELECT SUM(funcs_with_assembly) "
        "FROM Contract AS c "
        "JOIN SolidityFile as S ON c.file_id = s.file_id "
        "JOIN Address as a ON a.address_id = s.address_id "
        "WHERE a.nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} a.nr_token_transfers {comp_tk} {nr_tk} "
        "GROUP BY s.address_id"
    ),

    "assembly_lines_per_address": (
        "SELECT SUM(assembly_lines) "
        "FROM Contract AS c "
        "JOIN SolidityFile as S ON c.file_id = s.file_id "
        "GROUP BY s.address_id"
    ),
    "assembly_lines_per_address_filtered": (
        "SELECT SUM(assembly_lines) "
        "FROM Contract AS c "
        "JOIN SolidityFile as S ON c.file_id = s.file_id "
        "JOIN Address as a ON a.address_id = s.address_id "
        "WHERE a.nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} a.nr_token_transfers {comp_tk} {nr_tk} "
        "GROUP BY s.address_id"
    ),

    "contracts_per_address": (
        "SELECT COUNT(*) "
        "FROM Contract AS c "
        "JOIN SolidityFile as S ON c.file_id = s.file_id "
        "GROUP BY s.address_id"
    ),
    "contracts_per_address_filtered": (
        "SELECT COUNT(*) "
        "FROM Contract AS c "
        "JOIN SolidityFile as S ON c.file_id = s.file_id "
        "JOIN Address as a ON a.address_id = s.address_id "
        "WHERE a.nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} a.nr_token_transfers {comp_tk} {nr_tk} "
        "GROUP BY s.address_id"
    ),

    "fragments_per_address": (
        "SELECT COUNT(*) "
        "FROM Fragment as f "
        "JOIN Contract AS c ON f.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON s.file_id = c.file_id "
        "GROUP BY s.address_id"
    ),
    "fragments_per_address_filtered": (
        "SELECT COUNT(*) "
        "FROM Fragment as f "
        "JOIN Contract AS c ON f.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON s.file_id = c.file_id "
        "JOIN Address AS a ON a.address_id = s.address_id "
        "WHERE a.nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} a.nr_token_transfers {comp_tk} {nr_tk} "
        "GROUP BY s.address_id"
    ),

    "fragments_per_unique_address": (
        "SELECT COUNT(DISTINCT f.hash) "
        "FROM Address AS a "
        "JOIN SolidityFile AS s ON s.address_id = a.address_id "
        "JOIN Contract AS c ON c.file_id = s.file_id "
        "JOIN Fragment AS f ON f.contract_id = c.contract_id "
        "GROUP BY a.hash"
    ),
    "fragments_per_address_filtered": (
        "SELECT COUNT(DISTINCT f.hash) "
        "FROM Address AS a "
        "JOIN SolidityFile AS s ON s.address_id = a.address_id "
        "JOIN Contract AS c ON c.file_id = s.file_id "
        "JOIN Fragment AS f ON f.contract_id = c.contract_id "
        "WHERE a.nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} a.nr_token_transfers {comp_tk} {nr_tk} "
        "GROUP BY a.hash"
    ),

    "fragments_per_address_filter": (
        "SELECT COUNT(*) "
        "FROM Fragment as f "
        "JOIN Contract AS c ON f.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON s.file_id = c.file_id "
        "JOIN Address AS a ON a.address_id = s.address_id "
        "WHERE {char} {comp} {value} "
        "GROUP BY s.address_id"
    ),
    "fragments_per_address_filter_filtered": (
        "SELECT COUNT(*) "
        "FROM Fragment as f "
        "JOIN Contract AS c ON f.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON s.file_id = c.file_id "
        "JOIN Address AS a ON a.address_id = s.address_id "
        "WHERE {char} {comp} {value} "
        "AND (a.nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} a.nr_token_transfers {comp_tk} {nr_tk}) "
        "GROUP BY s.address_id"
    ),

    "instructions_in_addresses": (
        "SELECT s.address_id, i.{instr}_name, SUM(ipf.occurences) "
        "FROM {table_per} as ipf "
        "JOIN Fragment as f on f.fragment_id = ipf.fragment_id "
        "JOIN Contract AS c ON f.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON s.file_id = c.file_id "
        "JOIN {table} AS i ON i.{instr}_id = ipf.{instr}_id "
        "GROUP BY s.address_id, ipf.{instr}_id"
    ),
    "instructions_in_addresses_filtered": (
        "SELECT s.address_id, i.{instr}_name, SUM(ipf.occurences) "
        "FROM {table_per} as ipf "
        "JOIN Fragment as f on f.fragment_id = ipf.fragment_id "
        "JOIN Contract AS c ON f.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON s.file_id = c.file_id "
        "JOIN Address AS a ON a.address_id = s.address_id "
        "JOIN {table} AS i ON i.{instr}_id = ipf.{instr}_id "
        "WHERE a.nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} a.nr_token_transfers {comp_tk} {nr_tk} "
        "GROUP BY s.address_id, ipf.{instr}_id"
    ),

    "instructions_in_addresses_per_address": (
        "SELECT s.address_id, SUM(ipf.occurences) "
        "FROM {table_per} as ipf "
        "JOIN Fragment as f on f.fragment_id = ipf.fragment_id "
        "JOIN Contract AS c ON f.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON s.file_id = c.file_id "
        "JOIN {table} AS i ON i.{instr}_id = ipf.{instr}_id "
        "GROUP BY s.address_id"
    ),
    "instructions_in_addresses_per_address_filtered": (
        "SELECT s.address_id, SUM(ipf.occurences) "
        "FROM {table_per} as ipf "
        "JOIN Fragment as f on f.fragment_id = ipf.fragment_id "
        "JOIN Contract AS c ON f.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON s.file_id = c.file_id "
        "JOIN Address AS a ON a.address_id = s.address_id "
        "JOIN {table} AS i ON i.{instr}_id = ipf.{instr}_id "
        "WHERE a.nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} a.nr_token_transfers {comp_tk} {nr_tk} "
        "GROUP BY s.address_id"
    ),

    "instructions_per_fragment": (
        "SELECT f.fragment_id, SUM(ipf.occurences) "
        "FROM {table_per} as ipf "
        "JOIN Fragment as f on f.fragment_id = ipf.fragment_id "
        "JOIN {table} AS i ON i.{instr}_id = ipf.{instr}_id "
        "GROUP BY f.fragment_id, ipf.{instr}_id"
    ),
    "instructions_per_fragment_filtered": (
        "SELECT f.fragment_id, SUM(ipf.occurences) "
        "FROM {table_per} as ipf "
        "JOIN Fragment as f on f.fragment_id = ipf.fragment_id "
        "JOIN Contract AS c ON f.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON s.file_id = c.file_id "
        "JOIN Address AS a ON a.address_id = s.address_id "
        "JOIN {table} AS i ON i.{instr}_id = ipf.{instr}_id "
        "WHERE a.nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} a.nr_token_transfers {comp_tk} {nr_tk} "
        "GROUP BY f.fragment_id, ipf.{instr}_id"
    ),

    "instructions_per_unique_fragment": (
        "SELECT f.fragment_id, SUM(ipf.occurences) "
        "FROM {table_per} as ipf "
        "JOIN "
        "(SELECT fragment_id FROM Fragment GROUP BY hash) "
        "as f on f.fragment_id = ipf.fragment_id "
        "JOIN {table} AS i ON i.{instr}_id = ipf.{instr}_id "
        "GROUP BY f.fragment_id, ipf.{instr}_id"
    ),
    "instructions_per_unique_fragment_filtered": (
        "SELECT f.fragment_id, SUM(ipf.occurences) "
        "FROM {table_per} as ipf "
        "JOIN "
        "(SELECT fragment_id FROM Fragment as frag "
        "JOIN Contract AS c ON frag.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON s.file_id = c.file_id "
        "JOIN Address AS a ON a.address_id = s.address_id "
        "WHERE a.nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} a.nr_token_transfers {comp_tk} {nr_tk} "
        "GROUP BY frag.hash) "
        "as f on f.fragment_id = ipf.fragment_id "
        "JOIN {table} AS i ON i.{instr}_id = ipf.{instr}_id "
        "GROUP BY f.fragment_id, ipf.{instr}_id"
    ),

    "lines_per_fragment": (
        "SELECT fragment_id, lines FROM Fragment"
    ),

    "unique_fragments": (
        "SELECT COUNT(DISTINCT hash) FROM Fragment"
    ),
    "unique_fragments_filtered": (
        "SELECT COUNT(DISTINCT f.hash) FROM Fragment as f "
        "JOIN Contract AS c ON c.contract_id = f.contract_id "
        "JOIN SolidityFile AS s ON s.file_id = c.file_id "
        "JOIN Address AS a ON a.address_id = s.address_id "
        "WHERE a.nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} a.nr_token_transfers {comp_tk} {nr_tk} "
    ),

    "total_fragments": (
        "SELECT COUNT(*) FROM Fragment"
    ),
    "total_fragments_in": (
        "SELECT COUNT(*) FROM Fragment "
        "WHERE hash IN ({})"
    ),

    "unique_fragments_per_address": (
        "SELECT COUNT(DISTINCT hash) "
        "FROM Fragment as f "
        "JOIN Contract AS c ON f.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON s.file_id = c.file_id "
        "GROUP BY s.address_id"
    ),
    "unique_fragments_per_address_filtered": (
        "SELECT COUNT(DISTINCT f.hash) "
        "FROM Fragment as f "
        "JOIN Contract AS c ON f.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON s.file_id = c.file_id "
        "JOIN Address AS a ON a.address_id = s.address_id "
        "WHERE a.nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} a.nr_token_transfers {comp_tk} {nr_tk} "
        "GROUP BY s.address_id"
    ),

    "sum_per_fragment": (
        "SELECT f.fragment_id, SUM(i.occurences) "
        "FROM Fragment as f "
        "LEFT JOIN {table} as i ON f.fragment_id = i.fragment_id "
        "GROUP BY f.fragment_id"
    ),

    "addresses_characteristics": (
        "SELECT nr_transactions, unique_callers, nr_token_transfers, "
        "is_erc20, is_erc721, tvl, loc "
        "FROM Address"
    ),
    "addresses_characteristics_filtered": (
        "SELECT nr_transactions, unique_callers, nr_token_transfers, "
        "is_erc20, is_erc721, tvl, loc "
        "FROM Address "
        "WHERE nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} nr_token_transfers {comp_tk} {nr_tk}"
    ),

    "non_assembly_addresses_characteristics": (
        "SELECT nr_transactions, unique_callers, nr_token_transfers, "
        "is_erc20, is_erc721, tvl, loc "
        "FROM NonAssemblyAddress"
    ),
    "non_assembly_addresses_characteristics_filtered": (
        "SELECT nr_transactions, unique_callers, nr_token_transfers, "
        "is_erc20, is_erc721, tvl, loc "
        "FROM NonAssemblyAddress "
        "WHERE nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} nr_token_transfers {comp_tk} {nr_tk}"
    ),

    "blocks_assembly": (
        "SELECT block_number, COUNT(*) "
        "FROM Address "
        "GROUP BY block_number "
        "ORDER BY block_number ASC"
    ),
    "blocks_assembly_filtered": (
        "SELECT block_number, COUNT(*) "
        "FROM Address "
        "WHERE nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} nr_token_transfers {comp_tk} {nr_tk} "
        "GROUP BY block_number "
        "ORDER BY block_number ASC"
    ),

    "blocks_non_assembly": (
        "SELECT block_number, COUNT(*) "
        "FROM NonAssemblyAddress "
        "GROUP BY block_number "
        "ORDER BY block_number ASC"
    ),
    "blocks_non_assembly_filtered": (
        "SELECT block_number, COUNT(*) "
        "FROM NonAssemblyAddress "
        "WHERE nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} nr_token_transfers {comp_tk} {nr_tk} "
        "GROUP BY block_number "
        "ORDER BY block_number ASC"
    ),

    "compiler_assembly": (
        "SELECT solidity_version_etherscan "
        "FROM Address "
        "WHERE solidity_version_etherscan NOT LIKE 'vyper%'"
    ),
    "compiler_assembly_filtered": (
        "SELECT solidity_version_etherscan "
        "FROM Address "
        "WHERE solidity_version_etherscan NOT LIKE 'vyper%' "
        "AND (nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} nr_token_transfers {comp_tk} {nr_tk})"
    ),

    "compiler_non_assembly": (
        "SELECT solidity_version_etherscan "
        "FROM NonAssemblyAddress "
        "WHERE solidity_version_etherscan NOT LIKE 'vyper%'"
    ),
    "compiler_non_assembly_filtered": (
        "SELECT solidity_version_etherscan "
        "FROM NonAssemblyAddress "
        "WHERE solidity_version_etherscan NOT LIKE 'vyper%' "
        "AND (nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} nr_token_transfers {comp_tk} {nr_tk})"
    ),

    # The following query checks if an address contain only certain OPCODES
    # and declarations. Note that this query is slow.
    "addresses_containing_direct": (
        "SELECT COUNT(*) "
        "FROM ( "
            "SELECT s.address_id, SUM(opf.occurences) as t, SUM(dpf.occurences) as t2 "
            "FROM Fragment as f "
            "LEFT JOIN OpcodesPerFragment as opf ON f.fragment_id = opf.fragment_id "
            "LEFT JOIN DeclarationsPerFragment as dpf ON f.fragment_id = dpf.fragment_id "
            "JOIN Contract AS c ON f.contract_id = c.contract_id "
            "JOIN SolidityFile AS s ON s.file_id = c.file_id "
            "GROUP BY s.address_id "
            "HAVING (t - ( "
                "SELECT SUM(opf2.occurences) "
                "FROM Fragment as f2 "
                "LEFT JOIN OpcodesPerFragment as opf2 ON f2.fragment_id = opf2.fragment_id "
                "JOIN Contract AS c2 ON f2.contract_id = c2.contract_id "
                "JOIN SolidityFile AS s2 ON s2.file_id = c2.file_id "
                "WHERE s2.address_id = s.address_id "
                "AND opf2.opcode_id IN ({opcodes}) "
                "GROUP BY s2.address_id "
             ") = 0 OR t IS NULL) AND (t2 - ( "
                "SELECT SUM(dpf2.occurences) "
                "FROM Fragment as f3 "
                "LEFT JOIN DeclarationsPerFragment as dpf2 ON f3.fragment_id = dpf2.fragment_id "
                "JOIN Contract AS c3 ON f3.contract_id = c3.contract_id "
                "JOIN SolidityFile AS s3 ON s3.file_id = c3.file_id "
                "WHERE s3.address_id = s.address_id "
                "AND dpf2.declaration_id IN ({declarations}) "
                "GROUP BY s3.address_id "
             ") OR t2 IS NULL))"
    ),

    "addresses_containing": (
        "SELECT s.address_id "
        "FROM Fragment as f "
        "LEFT JOIN OpcodesPerFragment AS opf ON f.fragment_id = opf.fragment_id "
        "LEFT JOIN DeclarationsPerFragment AS dpf ON f.fragment_id = dpf.fragment_id "
        "LEFT JOIN OldOpcodesPerFragment AS old ON f.fragment_id = old.fragment_id "
        "LEFT JOIN HighLevelConstructsPerFragment AS hpf ON f.fragment_id = hpf.fragment_id "
        "JOIN Contract AS c ON f.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON c.file_id = s.file_id "
        "WHERE "
        "opf.opcode_id IN ({opcodes}) "
        "OR dpf.declaration_id IN ({declarations}) "
        "OR old.old_opcode_id IN ({old_opcodes}) "
        "OR hpf.high_level_construct_id IN ({high_level_constructs}) "
        "GROUP BY s.address_id"
    ),
    "addresses_containing_filtered": (
        "SELECT s.address_id "
        "FROM Fragment as f "
        "LEFT JOIN OpcodesPerFragment AS opf ON f.fragment_id = opf.fragment_id "
        "LEFT JOIN DeclarationsPerFragment AS dpf ON f.fragment_id = dpf.fragment_id "
        "LEFT JOIN OldOpcodesPerFragment AS old ON f.fragment_id = old.fragment_id "
        "LEFT JOIN HighLevelConstructsPerFragment AS hpf ON f.fragment_id = hpf.fragment_id "
        "JOIN Contract AS c ON f.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON c.file_id = s.file_id "
        "JOIN Address AS a ON a.address_id = s.address_id "
        "WHERE "
        "(a.nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} a.nr_token_transfers {comp_tk} {nr_tk}) "
        "AND (opf.opcode_id IN ({opcodes}) "
        "OR dpf.declaration_id IN ({declarations}) "
        "OR old.old_opcode_id IN ({old_opcodes}) "
        "OR hpf.high_level_construct_id IN ({high_level_constructs})) "
        "GROUP BY s.address_id"
    ),

    "top_x": (
        "SELECT instr "
        "FROM ("
            "SELECT s.address_id as a, pf.{id} as instr, SUM(pf.occurences) as t "
            "FROM Fragment as f "
            "LEFT JOIN {per_frag} as pf ON f.fragment_id = pf.fragment_id "
            "JOIN Contract AS c ON f.contract_id = c.contract_id "
            "JOIN SolidityFile AS s ON s.file_id = c.file_id "
            "GROUP BY s.address_id, pf.{id}) "
        "GROUP BY instr ORDER BY {aggr}(t) DESC LIMIT {limit}"
    ),
    "top_labels": (
        "SELECT l.label_name, COUNT(*) as t "
        "FROM AddressLabel AS al "
        "JOIN Label AS l ON al.label_id = l.label_id "
        "JOIN {table} AS a ON a.address = al.address "
        "GROUP BY l.label_id "
        "ORDER BY t DESC"
    ),
    "top_fragments": (
        "SELECT f.hash, COUNT(f.fragment_id) as total, f.code, f.start_line, "
        "f.end_line, c.contract_name, s.file_name, a.address, "
        "a.solidity_version_etherscan, a.block_number, 0, 0 "
        "FROM Fragment AS f "
        "JOIN Contract AS c ON f.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON c.file_id = s.file_id "
        "JOIN Address AS a ON s.address_id = a.address_id "
        "GROUP BY f.hash "
        "ORDER BY total DESC "
        "LIMIT {}"
    ),
    "top_fragments_transactions": (
        "SELECT f.hash, COUNT(f.fragment_id) as total, f.code, f.start_line, "
        "f.end_line, c.contract_name, s.file_name, a.address, "
        "a.solidity_version_etherscan, a.block_number, a.nr_transactions, 0 "
        "FROM Fragment AS f "
        "JOIN Contract AS c ON f.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON c.file_id = s.file_id "
        "JOIN Address AS a ON s.address_id = a.address_id "
        "GROUP BY f.hash "
        "ORDER BY a.nr_transactions DESC "
        "LIMIT {}"
    ),
    "top_fragments_unique_callers": (
        "SELECT f.hash, COUNT(f.fragment_id) as total, f.code, f.start_line, "
        "f.end_line, c.contract_name, s.file_name, a.address, "
        "a.solidity_version_etherscan, a.block_number, a.unique_callers, 0 "
        "FROM Fragment AS f "
        "JOIN Contract AS c ON f.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON c.file_id = s.file_id "
        "JOIN Address AS a ON s.address_id = a.address_id "
        "GROUP BY f.hash "
        "ORDER BY a.unique_callers DESC "
        "LIMIT {}"
    ),
    "top_fragments_contracts": (
        "SELECT t.hash, f.fcount, t.code, t.start_line, "
        "t.end_line, t.contract_name, t.file_name, t.address, "
        "t.solidity_version_etherscan, t.block_number, t.total_c, t.hash "
        "FROM ( "
            "SELECT f.hash, f.code, f.start_line, "
            "f.end_line, c.contract_name, s.file_name, a.address, "
            "a.solidity_version_etherscan, a.block_number, "
            "COUNT(a.address_id) as total_c, a.hash "
            "FROM Fragment AS f "
            "JOIN Contract AS c ON f.contract_id = c.contract_id "
            "JOIN SolidityFile AS s ON c.file_id = s.file_id "
            "JOIN Address AS a ON s.address_id = a.address_id "
            "GROUP BY a.hash, f.hash "
            "ORDER BY total_c DESC "
            "LIMIT {}"
        ") as t "
        "JOIN (SELECT hash, COUNT(*) as fcount "
               "FROM Fragment GROUP BY hash) AS f "
        "ON f.hash = t.hash"
    ),
    "random_fragments": (
        "SELECT f.hash, COUNT(f.fragment_id) as total, f.code, f.start_line, "
        "f.end_line, c.contract_name, s.file_name, a.address, "
        "a.solidity_version_etherscan, a.block_number, 0, 0 "
        "FROM Fragment AS f "
        "JOIN Contract AS c ON f.contract_id = c.contract_id "
        "JOIN SolidityFile AS s ON c.file_id = s.file_id "
        "JOIN Address AS a ON s.address_id = a.address_id "
        "GROUP BY f.hash "
        "ORDER BY RANDOM() "
        "LIMIT {}"
    ),

    "total_loc": (
        "SELECT SUM(loc) "
        "FROM {table}"
    ),
    "total_loc_filtered": (
        "SELECT SUM(loc) "
        "FROM {table} "
        "WHERE nr_transactions {comp_tx} {nr_tx} "
        "{filters_cond} nr_token_transfers {comp_tk} {nr_tk}"
    ),

    "total_loc_from_unique": (
        "SELECT SUM(loc) FROM ("
            "SELECT loc "
            "FROM {table} "
            "GROUP BY hash"
        ")"
    ),
    "total_loc_from_unique_filtered": (
        "SELECT SUM(loc) FROM ("
            "SELECT loc "
            "FROM {table} "
            "WHERE nr_transactions {comp_tx} {nr_tx} "
            "{filters_cond} nr_token_transfers {comp_tk} {nr_tk} "
            "GROUP BY hash"
        ")"
    ),

    "start_block": (
        "SELECT min(block_number) FROM {table}"
    ),
    "start_block_filtered": (
       "SELECT min(block_number) FROM {table} "
       "WHERE nr_transactions {comp_tx} {nr_tx} "
       "{filters_cond} nr_token_transfers {comp_tk} {nr_tk} "
    ),

    "end_block": (
        "SELECT max(block_number) FROM {table} WHERE block_number != ''"
    ),
    "end_block_filtered": (
       "SELECT max(block_number) FROM {table} WHERE block_number != '' "
       "WHERE nr_transactions {comp_tx} {nr_tx} "
       "{filters_cond} nr_token_transfers {comp_tk} {nr_tk} "
    )
}
