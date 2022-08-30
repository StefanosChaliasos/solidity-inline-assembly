Artifact for "A Study of Inline Assembly in Solidity Smart Contracts" 
=====================================================================

This is the artifact for the OOPSLA'22 paper titled 
"A Study of Inline Assembly in Solidity Smart Contracts".

* Stefanos Chaliasos, Arthur Gervais, and Benjamin Livshits. 2022
A Study of Inline Assembly in Solidity Smart Contracts.
In Proceedings of the ACM on Programming Languages (OOPSLA '22), 
2022, Auckland, New Zealand, XX pages. 
([doi:XX.XXXX/XXXXXXX](https://doi.org/XX.XXXX/XXXXXXX))

An archived version of the artifact is also available on Zenodo. 
See <https://doi.org/10.5281/zenodo.6807330>.

__IMPORTANT NOTE:__ Before running any of the following commands, first move to
the project directory (e.g., `cd solidity-inline-assembly`).

# Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Setup](#setup)
- [Download Database](#download-database)
- [Database Description](#database-description)
- [Dataset (Optionally)](#dataset-optionally)
- [Getting Started](#getting-started)
  * [Query the Database](#query-the-database)
  * [Get Dataset Details](#get-dataset-details)
- [Step by Step Instructions](#step-by-step-instructions)
  * [Data Collection (Section 3.1)](#data-collection-section-31)
  * [Quantitatively Study Inline Assembly On Solidity Smart Contracts (Section 4)](#quantitatively-study-inline-assembly-on-solidity-smart-contracts-section4)
    + [RQ1: Measuring Inline Assembly (Section 4.1)](#rq1-measuring-inline-assembly-section-41)
    + [RQ2: Smart Contract Characteristics (Section 4.2)](#rq2-smart-contract-characteristics-section-42)
    + [RQ3: Evolution of Inline Assembly (Section 4.3)](#rq3-evolution-of-inline-assembly-section-43)
    + [RQ4: A Taxonomy of Inline Assembly (Section 4.4)](#rq4-a-taxonomy-of-inline-assembly-section-44)
- [Extras (Optionally)](#extras-optionally)
  * [Instructions to Detect Contract Addresses](#instructions-to-detect-contract-addresses)
  * [Query Google Big Query to Get Contract Data](#query-google-big-query-to-get-contract-data)
  * [Analyze X Contracts From Scratch](#analyze-x-contracts-from-scratch)
    + [Data Collection](#data-collection)
    + [Post Filtering](#post-filtering)
    + [Source Code Analysis](#source-code-analysis)
    + [Feed Results into the Database](#feed-results-into-the-database)
    + [Print Results](#print-results)
  * [Analyze Single Smart Contract for Inline Assembly Fragments](#analyze-single-smart-contract-for-inline-assembly-fragments)

# Overview

The purpose of this artifact is 
(1) to reproduce the results presented in our paper, 
(2) to document our dataset in order to facilitate further research, 
and (3) to document and make available some additional resources to help 
researchers build on top of this artifact ([Extras](#extras-optionally)). 
Specifically, the artifact has the following structure:

* `scripts/`: This is the directory that contains the scripts needed to reproduce 
the results, the figures, and the tables presented in our paper.
In addition, it contains scripts to download and analyze solidity code.
* `scripts/schema.sql`: This is the database schema that was used to analyze
inline assembly fragments.
* `data/labels.json`: A JSON file containing Etherscan labels.
* `figures/`:  This directory will be used to save the figures of our paper.
* `figures/schema.jpg`:  The schema of our database.
* `Dockerfile`: The Dockerfile used to create a Docker image of our artifact. 
This image contains all dependencies.

All our scripts provide a CLI and a `-h` option to show a help message.

For the database used for performing the analyses presented on our OOPSLA'22
paper, check the [Download Database](#download-database) and
[Database Description](#database-description) sections of this artifact.
For information about the complete dataset, check 
the [Dataset](#dataset-optionally) section.

The first contract in our dataset/database is from block `47205` (Aug-07-2015)
and the last from block `14339858` (Mar-07-2022).

# Requirements

See [REQUIREMENTS.md](./REQUIREMENTS.md).

# Setup

See [SETUP.md](./SETUP.md).


# Download Database

See [DATABASE.md](./DATABASE.md).

# Database Description

![Schema ER Diagram](https://github.com/StefanosChaliasos/solidity-inline-assembly/blob/main/figures/schema.jpg?raw=true)

We provide an SQLite database (see the file `database/inline.db`) that contains
all the information needed for the quantitative analysis.
This database is initialized based on the SQL script stored into
`scripts/schema.sql`. The database consists of the following tables:

* `NonAssemblyAddress`: The addresses of all contracts that do not use
inline assembly.
  - `address_id`: A serial number corresponding to the ID of the address.
  - `address`: The hexadecimal representation of the address.
  - `nr_transactions`: The number of transactions of the address.
  - `unique_callers`: The number of unique addresses that have interacted with the address.
  - `nr_token_transfers`: The number of the token transfers of the address.
  - `is_erc20`: A boolean value declaring if the contract implements the ERC20 standard.
  - `is_erc721`: A boolean value declaring if the contract implements the ERC721 standard.
  - `tvl`: The balance of the address.
  - `solidity_version_ethercan`: The compiler version used to compile the contract if available on Etherscan.
  - `evm_version`: The version of the bytecode if available on Etherscan.
  - `block_number`: The block number that the contract was created (i.e., its timestamp).
  - `loc`: The number of lines of code of the contract.
  - `hash`: A SHA256 hash of the code of the contract.
* `Label`: Labels from Etherscan.
  - `label_id`: A serial number corresponding to the ID of the label.
  - `label_name`: The name of the label.
* `AddressLabel`: A label of an `Address` or `NonAssemblyAddress`.
  - `al_id`: A serial number corresponding to the ID of the address label.
  - `address`:  The hexadecimal representation of an address.
  - `address_type`: The type of the address (e.g., account).
  - `tag`: The Etherscan tag of the address.
* `Address`: The addresses of all contracts that use inline assembly.
  - This table has the same fields as `NonAssemblyAddress` table.
* `SolidityFile`: The solidity files that contain the source code of an `Address`.
  - `file_id`: A serial number corresponding to the ID of the Solidity file.
  - `file_name`: The name of the Solidity file.
  - `lines`: The number of lines of the file.
  - `solidity_version`: The Solidity version extracted by the `pragma` directive.
  - `address_id`: A foreign key to the `Address` table.
* `Contract`: The contracts that are declared into one `SolidityFile`.
  - `contract_id`: A serial number corresponding to the ID of the contract.
  - `contract_name`: The name of the contract.
  - `lines`: The number of lines of the contract.
  - `funcs`: The number of the functions of the contract.
  - `funcs_with_assembly`: The number of functions that contain inline assembly.
  - `assembly_fragments`: The number of inline assembly fragments into the contract.
  - `assembly_lines`: The number of lines of assembly code in the contract.
  - `has_assembly`: A boolean value declaring if the contract contains inline assembly.
  - `file_id`: A foreign key to the `SolidityFile` table.
* `Fragment`: The inline assembly fragments of `Contract`s.
  - `fragment_id`: A serial number corresponding to the ID of the fragment.
  - `lines`: The lines of code of the fragment.
  - `start_line`: The line of the contract that the fragment start.
  - `end_line`: The line of the contract that the fragment end.
  - `hash`: The SHA256 hash of the code of the fragment.
  - `contract_id`: A foreign key to the `Contract` table.

Furthermore, the database contains five more tables that include the number of
occurrences of specific opcodes or instructions in an inline assembly 
fragment. Each of those tables is connected with another table that 
declares the names for each opcode or instructions.
The names of the tables are:

* `HighLevelConstructsPerFragment`: Includes YUL high level constructs (e.g., `for`).
* `DeclarationsPerFragment`: Includes YUL declarations (e.g., `if`).
* `SpecialOpcodesPerFragment`: Includes special YUL opcodes (e.g., `datasize`).
* `OldOpcodesPerFragment`: Includes opcodes that are not available in YUL,
but were used before the introduction of YUL (e.g., `swap`).
* `OpcodesPerFragment`: Includes all EVM opcodes that are available in YUL (e.g., `load`).

Each of those tables has the following fields (we will use `OpcodesPerFragment`
as an example):
* `opf_id`: A serial number corresponding to the ID of the opcodes per fragment.
* `fragment_id`: A foreign key to the `Fragment` table.
* `opcode_id`: A foreign key to the `Opcode` table.
* `occurrences`: The number of occurrences of the opcode in this fragment.

The tables that provide the names for each instruction/opcode are
`HighLevelConstruct`, `Declaration`, `SpecialOpcode`, 
`OldOpcode`, and `Opcode`.

# Dataset (Optionally)

See [DATASET.md](./DATASET.md).

# Getting Started

__Total time:__ less than 30 minutes (depending on your internet connection).

Before proceeding to this section, make sure you have followed the instructions in
[Setup](#Setup) and [Download Database](#download-database) sections.

Let's start by validating that all the required data have been downloaded.

```bash
ls database
```

The result of this command should be:

```
contract_addresses.csv inline.db
```

We will use the Docker image (namely `solidity-inline-assembly`) built by the 
instructions from the [Setup](#setup) guide to getting started. Recall that this 
image contains all the required packages needed for reproducing our 
results.

You can enter a new container by using the following command:

```bash
docker run -ti --rm \
  -v $(pwd)/database:/home/inline/database \
  -v $(pwd)/figures:/home/inline/figures \
  solidity-inline-assembly
```

Otherwise, you can install all dependencies of our artifact in your local 
machine by following the instructions on the [Setup](#setup) guide.

## Query the Database

From inside the container, we can perform some basic queries on our database.

Get the total number of contracts without inline assembly.

```
inline@a9cc16b080f9:~$ sqlite3 database/inline.db "SELECT COUNT(*) FROM NonAssemblyAddress"
5268551
```

Get the total number of contracts containing inline assembly with more than 10 transactions.

```
inline@a9cc16b080f9:~$ sqlite3 database/inline.db "SELECT COUNT(*) FROM Address WHERE nr_transactions > 10"
136048
```

Get the sum of balances of all contracts that contain inline assembly.

```
inline@a9cc16b080f9:~$ sqlite3 database/inline.db "SELECT SUM(tvl) FROM Address"
4774806.1840864
```

Count all contracts that contain inline assembly fragments.

```
inline@a9cc16b080f9:~$ sqlite3 database/inline.db "SELECT COUNT(*) FROM Contract WHERE has_assembly = 'True'"
2048336
```

Get the address of 10 smart contracts that use the `extcodesize` OPCODE.

* Command

```
# ~10 seconds
inline@a9cc16b080f9:~$ sqlite3 database/inline.db "SELECT a.address FROM Address AS a JOIN SolidityFile AS s ON a.address_id = s.address_id JOIN Contract AS c ON s.file_id = c.file_id JOIN Fragment AS f ON c.contract_id = f.contract_id JOIN OpcodesPerFragment AS o ON f.fragment_id = o.fragment_id JOIN Opcode AS op ON o.opcode_id = op.opcode_id WHERE op.opcode_name = 'extcodesize' GROUP BY a.address LIMIT 10"
0x0000000000051b0e35293cafaa205f461cd1fbb6
0x00000000000b7f8e8e8ad148f9d53303bfe20796
0x00000000001e980d286be7f5f978f4cc33128202
0x00000000002226c940b74d674b85e4be05539663
0x000000000037d42ab4e2226ce6f44c5dc0cf5b16
0x000000000041d7d38b9061e1aa93f014f2f28393
0x00000000004cda75701eea02d1f2f9bdce54c10d
0x0000000000796dc3aa12eb9fe3b6e8f4d92cc966
0x00000000008a10a98969a000d1c0aba90f858d6a
0x000000000092c287eb63e8c2c30b4a74787054f8
```

* SQL Query

```
SELECT a.address 
FROM Address AS a
JOIN SolidityFile AS s ON a.address_id = s.address_id
JOIN Contract AS c ON s.file_id = c.file_id
JOIN Fragment AS f ON c.contract_id = f.contract_id
JOIN OpcodesPerFragment AS o ON f.fragment_id = o.fragment_id
JOIN Opcode AS op ON o.opcode_id = op.opcode_id
WHERE op.opcode_name = 'extcodesize'
GROUP BY a.address
LIMIT 10
```

## Get Dataset Details

Here we just check that the `db_queries.py` script works properly by printing 
statistics about the dataset.

```bash
TOTAL=$(cat database/contract_addresses.csv | wc -l | xargs)
# ~10 seconds
inline@a9cc16b080f9:~$ python scripts/db_queries.py database/inline.db --total-contracts $TOTAL
Source statistics
-----------------

--------------------------------------------------------------------------------
Solidity source available: 6962185 (55%)
Solidity source not available: 5512896 (44%)
LOC: 722666226
--------------------------------------------------------------------------------
Unique Solidity Contracts: 110457 (1%)
LOC of Unique Solidity Contracts: 55801418
--------------------------------------------------------------------------------
```

Now, you can exit the Docker container by running:

```
exit
```

# Step by Step Instructions

__NOTE__: Remember to run all the subsequent docker run commands from the root 
directory of the artifact (i.e., `solidity-inline-assembly`).

To validate the main results presented in the paper, you can create a new Docker 
container by running the following command. Otherwise, make sure you have 
followed the instructions in the [Setup](#setup) guide to install everything
locally.

```
docker run -ti --rm \
  -v $(pwd)/database:/home/inline/database \
  -v $(pwd)/figures:/home/inline/figures \
  -v $(pwd)/data:/home/inline/data \
  solidity-inline-assembly
```

In the following section, we provide instructions for reproducing the results 
presented in the paper using the data from the SQLite database 
in `database/inline.db`.

## Data Collection (Section 3.1)

Run the following scripts to print statistics related to our dataset. 
Specifically, the scripts reproduces Figure 3.

```bash
#~8 minutes
inline@a9cc16b080f9:~$ ./scripts/get_statistics.sh database/contract_addresses.csv
```

The above script prints the following, i.e., the first 7 lines of Figure 3.

```
------------------------------------------------------------------------
Start Block: 47205
End Block: 14339858
------------------------------------------------------------------------
Contracts with at least one transaction: 5761898
Contracts with at least one token transfer: 8794332
Contracts with at least one transaction or token transfer: 12475080
------------------------------------------------------------------------
```

__NOTE:__ This script does not print the "Total Contracts" and 
"Contracts without a transaction or token transfer" rows because they 
are not part of our dataset. 

Proceed with the next script:

```bash
inline@a9cc16b080f9:~$ TOTAL=$(cat database/contract_addresses.csv | wc -l | xargs)
# ~10 seconds
inline@a9cc16b080f9:~$ python scripts/db_queries.py database/inline.db --total-contracts $TOTAL
```

The above script prints the following, i.e., the last 5 lines of Figure 3.

```
Source statistics
-----------------

--------------------------------------------------------------------------------
Solidity source available: 6851728 (54%)
Solidity source not available: 5623353 (45%)
LOC: 722666226
--------------------------------------------------------------------------------
Unique Solidity Contracts: 159241 (2%)
LOC of Unique Solidity Contracts: 55801418
--------------------------------------------------------------------------------
```

__NOTE__: In the submitted draft of the paper, there is a typo in the table,
and in place of "Solidity source not available" it should be "Solidity source
available" and vice versa.

## Quantitatively Study Inline Assembly On Solidity Smart Contracts (Section 4)

For each RQ, we have implemented an option on `scripts/db_queries.py` to 
print the results for the respective RQ. In the following, we'll provide 
instructions on how to execute each script, what it prints, and what to check
against the paper.

### RQ1: Measuring Inline Assembly (Section 4.1)

```
#~5 minutes
inline@a9cc16b080f9:~$ python scripts/db_queries.py database/inline.db --rq1
```

This script prints the following.

```

RQ1: Measuring Inline Assembly
------------------------------


--Density of inline assembly fragments--
One fragment per 212 LOCS
----------------------------------------

Saving cumulative distribution at figures/fragments_cum.pdf

5388/3427424 (0%) fragments are unique

Saving histogram at figures/instructions_hist.pdf

                          Statistics Table
===================================================================
                                                              Total
-------------------------------------------------------------------
Total Contracts                                               6.8 M
Total Contracts using Inline Assembly                  1583177 (23%)
Total Unique Contracts                                      159.2 K
Total Unique Contracts using Inline Assembly            62848 (39%)
Total Inline Assembly Fragments                               3.4 M
Total Inline Assembly Fragments in Unique Addresses         176.9 K
Total Inline Assembly Unique Fragments                        5.3 K
Total Instructions                                           33.7 M

                                        Fragments and Instructions Table
================================================================================================================
                                               total         max         min        mean      median          sd
----------------------------------------------------------------------------------------------------------------
Fragments per contract                         3.4 M          81           1        2.16           2        3.57
Unique fragments per contract                  3.2 M          53           1        2.08           2        2.93
Instructions per fragment                     33.7 M       4.0 K           1        9.94           8        9.44
Instructions per unique fragment              56.2 K       4.0 K           1       10.62           4       63.52
```

The claims of the paper that are supported by that script are:

* Figure 4 -> Statistics Table
* Figure 5 -> Fragments and Instructions Table
* Figure 6 -> `figures/fragments_cum.pdf`
* Figure 7 -> `figures/instructions_hist.pdf`
* Statement on line 408 about unique fragments -> 5388/3427424 (0%) fragments are unique
* Statement on line 431 about fragments per LOC -> One fragment per 212 LOCS

### RQ2: Smart Contract Characteristics (Section 4.2)

```
#~5 minutes
inline@a9cc16b080f9:~$ python scripts/db_queries.py database/inline.db --rq2
```

This script prints the following.

```
RQ2: Smart Contract Characteristics
-----------------------------------

Saving figures/comp_nr_transactions.pdf
Saving figures/comp_unique_callers.pdf
Saving figures/comp_nr_token_transfers.pdf

                                              Characteristics
============================================================================================================
                                           total         max         min        mean      median          sd
------------------------------------------------------------------------------------------------------------
Non Assembly nr_transactions             511.9 M     126.7 M           0       97.16           0      60.7 K
Assembly nr_transactions                 230.6 M      19.5 M           0         145           1      23.6 K
Non Assembly unique_callers               86.5 M      18.2 M           0       16.42           0       8.2 K
Assembly unique_callers                   59.2 M       5.6 M           0       37.45           1       5.4 K
Non Assembly nr_token_transfers          139.2 M      37.1 M           0       26.42           2      16.5 K
Assembly nr_token_transfers              302.9 M       8.1 M           0         191           2      13.7 K
Non Assembly tvl                          20.7 M       9.8 M           0        3.94           0       5.3 K
Assembly tvl                               4.7 M     572.7 K           0        3.01           0         879
Non Assembly loc                         328.5 M       9.4 K           0       62.36          40       67.53
Assembly loc                             394.1 M      14.1 K           0         248         161         511

                                                 Fragments
===========================================================================================================
                                          total         max         min        mean      median          sd
-----------------------------------------------------------------------------------------------------------
When a.nr_transactions > 50000            1.7 K          38           1        4.12           2        5.44
When a.nr_transactions <= 50000           3.4 M          81           1        2.16         2.0        3.57


----------ERC20 and ERC721----------
Non Assembly ERC20 percentage: 1.3%
Assembly ERC20 percentage: 0.093%
Non Assembly ERC721 percentage: 0.0067%
Assembly ERC721 percentage: 0.024%
------------------------------------
```

The claims of the paper that are supported by that script are:

* Figure 8 -> `figures/comp_nr_transactions.pdf`
* Figure 9 -> `figures/comp_unique_callers.pdf`
* Figure 10 -> `figures/comp_nr_token_transfers.pdf`
* Figure 11 -> Characteristics
* Figure 12 -> ERC20 and ERC721
* Statement on line 522 about mean inline assembly fragments when tx > 50K and tx <= 50K -> Fragments

### RQ3: Evolution of Inline Assembly (Section 4.3)

```
#~30 seconds
inline@a9cc16b080f9:~$ python scripts/db_queries.py database/inline.db --rq3
```

This script prints the following.

```
RQ3: Evolution of Inline Assembly
---------------------------------

Saving result to figures/evolution_blocks.pdf

     Percentages per compiler version
=========================================
     non assembly    assembly        perc
-----------------------------------------
1              13           0           0
2              99           0           0
3           4.1 M          37           0
4           1.0 M     489.1 K          32
5          39.0 K     219.2 K          84
6          12.7 K      66.4 K          83
7           7.6 K     748.3 K          98
8          22.3 K      59.8 K          72
```

The claims of the paper that are supported by that script are:

* Figure 13 -> `figures/evolution_blocks.pdf`
* Figure 14 -> Percentages per compiler version

### RQ4: A Taxonomy of Inline Assembly (Section 4.4)

```
#~12 minutes
inline@a9cc16b080f9:~$ python scripts/db_queries.py database/inline.db --rq4
```

This script prints the following.

```
RQ4: A Taxonomy of Inline Assembly
----------------------------------

### Arithmetic Operations ###

                 Arithmetic Operations
========================================================
                            perc         occ       total
--------------------------------------------------------
add                        80.22       1.2 M       7.6 M
sub                         7.75     122.7 K     244.0 K
exp                         1.78      28.2 K      77.6 K
div                         1.12      17.6 K     125.2 K
mul                         0.92      14.6 K     116.7 K
mod                         0.70      11.1 K      20.8 K
mulmod                      0.06         942     111.8 K
addmod                      0.00          64       1.0 K
sdiv                        0.00           2          24
signextend                  0.00           2          40
smod                           0           0           0


#############################

### Comparison and Bitwise Logic Operations ###

                       Comparison
========================================================
                            perc         occ       total
--------------------------------------------------------
eq                         49.27     780.0 K       1.6 M
lt                          1.98      31.2 K     115.2 K
gt                          1.88      29.8 K      35.1 K
slt                         0.04         685         702
sgt                         0.00          63         190

                     Bitwise Logic
========================================================
                            perc         occ       total
--------------------------------------------------------
and                        68.24       1.0 M       1.2 M
iszero                      7.94     125.7 K     282.1 K
byte                        3.09      48.8 K      69.5 K
shr                         2.04      32.2 K      59.8 K
or                          1.64      25.9 K      48.3 K
not                         1.31      20.7 K      43.9 K
xor                         0.35       5.5 K      10.2 K
shl                         0.19       3.0 K      22.2 K
sar                         0.00          21          36


###############################################

### Hashing Operations ###

                       KECCAK256
========================================================
                            perc         occ       total
--------------------------------------------------------
keccak256                   0.96      15.2 K     109.8 K
sha3                        0.01         172       1.3 K


##########################

### Enviromental Information ###

                  Current Environment
========================================================
                            perc         occ       total
--------------------------------------------------------
gas                        23.51     372.2 K     411.7 K
returndatasize             16.91     267.6 K     620.4 K
returndatacopy             16.89     267.4 K     289.2 K
calldatasize               15.15     239.8 K     482.4 K
calldatacopy               15.09     238.8 K     241.6 K
calldataload                8.45     133.8 K     231.6 K
chainid                     5.43      85.9 K      87.8 K
address                     0.75      11.9 K      12.0 K
codesize                    0.33       5.2 K       5.2 K
codecopy                    0.33       5.2 K       5.2 K
callvalue                   0.22       3.4 K       6.0 K
caller                      0.17       2.6 K       2.8 K
origin                      0.00          16          16
selfbalance                 0.00          11          44
gasprice                    0.00           9          17

                  Account Information
========================================================
                            perc         occ       total
--------------------------------------------------------
extcodecopy                44.97     712.0 K     712.0 K
extcodesize                12.84     203.3 K     226.9 K
extcodehash                 3.26      51.6 K      51.7 K
balance                     0.56       8.8 K       8.8 K


################################

### Block Information ###

                   Block Information
========================================================
                            perc         occ       total
--------------------------------------------------------
timestamp                   0.85      13.5 K      13.5 K
number                      0.30       4.6 K       4.6 K
blockhash                   0.30       4.6 K       4.6 K
coinbase                    0.29       4.6 K       4.6 K
difficulty                  0.00           1           1
gaslimit                       0           0           0


#########################

### Stack, Memory, and Storage Operations ###

                         Stack
========================================================
                            perc         occ       total
--------------------------------------------------------
pop                         0.24       3.8 K       7.8 K
pc                             0           0           0

                         Memory
========================================================
                            perc         occ       total
--------------------------------------------------------
mload                      85.32       1.3 M       6.6 M
mstore                     48.92     774.4 K       4.6 M
mstore8                     0.29       4.5 K      37.4 K
msize                       0.26       4.1 K       4.1 K

                        Storage
========================================================
                            perc         occ       total
--------------------------------------------------------
sload                       8.22     130.1 K     190.0 K
sstore                      3.17      50.2 K     145.6 K


#############################################

### Flow Operations ###

                    YUL Control Flow
========================================================
                            perc         occ       total
--------------------------------------------------------
switch                     21.35     337.9 K     484.0 K
if                          4.76      75.3 K     181.4 K
for                         1.78      28.2 K      85.0 K
leave                          0           0           0

                  Control Flow Opcodes
========================================================
                            perc         occ       total
--------------------------------------------------------
jumpi                       0.07       1.0 K       1.3 K
jump                        0.01         117         118
jumpdest                       0           0           0


#######################

### System Operations ###

                          Call
========================================================
                            perc         occ       total
--------------------------------------------------------
delegatecall               21.36     338.2 K     340.9 K
call                        2.64      41.7 K      49.8 K
staticcall                  1.39      21.9 K      26.3 K
callcode                       0           0           0

                         Create
========================================================
                            perc         occ       total
--------------------------------------------------------
create2                    45.09     713.8 K     714.4 K
create                      6.58     104.1 K     104.4 K

                       Execution
========================================================
                            perc         occ       total
--------------------------------------------------------
revert                     28.59     452.6 K     686.5 K
return                     15.77     249.6 K     290.4 K
stop                        0.15       2.3 K       2.3 K
selfdestruct                0.00           4           7

                        Invalid
========================================================
                            perc         occ       total
--------------------------------------------------------
invalid                     0.04         640       1.7 K


#########################

### YUL Declarations ###

                    YUL Declarations
========================================================
                            perc         occ       total
--------------------------------------------------------
let                        73.24       1.1 M       3.5 M
function                    0.00          49         113


########################

### Push, Duplication, and Exchange Operations ###

            Push, Duplication, and Exchange
========================================================
                            perc         occ       total
--------------------------------------------------------
swap                        0.00           4          12
push                           0           0           0
dup                            0           0           0


##################################################

### Logging Operations ###

                   Logging Operations
========================================================
                            perc         occ       total
--------------------------------------------------------
log1                        0.18       2.8 K       2.8 K
log4                        0.05         809         820
log3                        0.03         548         569
log2                        0.03         541         541
log0                        0.03         539         539


##########################

### YUL Special Instructions ###

                YUL Special Instructions
========================================================
                            perc         occ       total
--------------------------------------------------------
datasize                    0.00           1           1
dataoffset                     0           0           0
datacopy                       0           0           0
setimmutable                   0           0           0
loadimmutable                  0           0           0
linkersymbol                   0           0           0
memoryguard                    0           0           0
verbatim                       0           0           0


################################

                    Instruction groups
=========================================================
                                                     perc
---------------------------------------------------------
Stack, Memory, and Storage Operations               90.94
Enviromental Information                            80.86
Arithmetic Operations                               80.31
Comparison and Bitwise Logic Operations             77.91
System Operations                                   74.16
YUL Declarations                                    73.24
Flow Operations                                     24.17
Hashing Operations                                   0.97
Block Information                                    0.85
Logging Operations                                   0.20
Push, Duplication, and Exchange Operations           0.00
YUL Special Instructions                              0.0
```

The claims of the paper that are supported by that script are:

* Figure 15 -> Arithmetic Operations
* Figure 16 -> Comparison and Bitwise Logic Operations
* Figure 19 -> Hashing Operations
* Figure 20 -> Enviromental Information
* Figure 21 -> Block Information
* Figure 22 -> Stack, Memory, and Storage Operations
* Figure 23 -> Flow Operations
* Figure 24 -> System Operations
* Figure 25 -> YUL Declarations
* Figure 26 -> Logging Operations
* The percentage in the parentheses on the title of each subsection 4.4.X -> Instruction groups
* Figure 27 -> `figures/taxonomy_categories.pdf`

# Extras (Optionally)

## Instructions to Detect Contract Addresses

__Note:__ In this section, we crawl an Ethereum archive node to detect which 
addresses are smart contracts; thus, you will need access to an archive node to 
run the following script.

* Requirements:
  - An installation of the `Go` language,
  - A `geth` archive node.

* Description

Our crawler is able to detect transactions that have been created both by 
EOA addresses or by other smart contracts. To enable the latter, we employ 
a tracer which makes the crawling much slower.

* Instructions

The following command will crawl all blocks from block number XXX  until block 
number YYY. The script will produce `geth_contracts.csv` containing contract 
addresses. Note that for blocks after `12965000`, you need to use 
`github.com/ethereum/go-ethereum v1.10.16`.

```bash
go mod tidy
go run go-src/cmd/get_contract_addresses/main.go --startblock XXX --endblock YYY
```

## Query Google Big Query to Get Contract Data

We query [Google Big Query](https://console.cloud.google.com/bigquery)
to get the addresses of contracts deployed on 
Ethereum and retrieve specific metadata. Our study excludes contracts that have 
never been used, i.e., they have not any transaction or token transfer. 
Furthermore, for each contract address, we gather the following metadata: 
`transactions count`, `unique callers`, `token transfers count`, `balance`, 
`is erc20`, `is erc721`, and `block number`. 

To do so, we first use the `bigquery-public-data.crypto_ethereum`
database to get aggregate values per address for transactions count, unique 
callers, and token transfers count. Then we save them to new tables. 
For example, to get the total transactions per address, we perform the 
following query. 

```sql
SELECT contracts.address, COUNT(1) AS tx_count
FROM `crypto_ethereum.contracts` as contracts
JOIN `crypto_ethereum.transactions` AS transactions
ON (transactions.to_address = contracts.address)
GROUP BY contracts.address
```

Having created the following six new tables for contract addresses: 
`Contracts`, `Balances`, `ContractsTransactions`, `TokenTransfersFrom`, 
`TokenTransfersTo`, and `UniqueCallers`, we proceed by running the 
following query to gather our dataset composing of all contract addresses and 
their metadata.

```sql
SELECT contracts.address, transactions.tx_count, unique_callers.unique_callers,
token_transfers_from.tx_count + token_transfers_to.tx_count as token_transfers,
balances.balance, contracts.is_erc20, contracts.is_erc721, contracts.block_number
FROM `assembly.Contracts` AS contracts
LEFT OUTER JOIN `assembly.Balances` AS balances
ON (balances.address = contracts.address)
LEFT OUTER JOIN `assembly.ContractsTransactions` AS transactions
ON (transactions.address = contracts.address)
LEFT OUTER JOIN `assembly.TokenTransfersFrom` AS token_transfers_from
ON (token_transfers_from.address = contracts.address)
LEFT OUTER JOIN `assembly.TokenTransfersTo` AS token_transfers_to
ON (token_transfers_to.address = contracts.address)
LEFT OUTER JOIN `assembly.UniqueCallers` AS unique_callers
ON (unique_callers.address = contracts.address)
WHERE transactions.tx_count > 0 OR
token_transfers_from.tx_count + token_transfers_to.tx_count > 0
```

## Analyze X Contracts From Scratch

#### Run with Docker

If you run the following using Docker, mount `data` and `sample_dataset` to 
your local file system.

```
mkdir -p sample_dataset
docker run -ti --rm \
  -v $(pwd)/database:/home/inline/database \
  -v $(pwd)/figures:/home/inline/figures \
  -v $(pwd)/data:/home/inline/data \
  -v $(pwd)/sample_dataset:/home/inline/sample_dataset \
  solidity-inline-assembly
```

This section provides the instruction to analyze 50 contracts.
We will first download the source code of 50 random contract addresses, 
then process them to detect and analyze any inline assembly fragments, 
and finally, feed the results into a database. We can then use this database 
for performing the [quantitative analysis](#quantitatively-study-inline-assembly-on-solidity-smart-contracts-section4#).

Before continuing, you will need to generate an API key for <https://etherscan.io>, 
the blockchain explorer we'll use to get the source code of the contracts.
You can follow [this link](https://info.etherscan.com/etherscan-developer-api-key/)
(note that you will need to create an account first) to generate a key.

After generating that key, set a shell variable, namely `API_KEY`.

```bash
inline@a9cc16b080f9:~$ API_KEY=<YOUR_API_KEY>
```

### Dataset Collection

1. Set target directory to `sample_dataset`.

```bash
inline@a9cc16b080f9:~$ TARGET=sample_dataset
```

2. Get a sample dataset of contract addresses.

To do so, we will randomly select 50 addresses from `database/contract_addresses.csv`.

__NOTE__: If you want to analyze all contracts of `database/contract_addresses.csv`,
you can copy this file to `$TARGET/database.csv`. To analyze all addresses,
we split the file into 5 different files, and we used 5 commodity servers.
For the "Feed Results into the Database" commands, we copied everything to a 
machine with enough disk space and 200GB RAM. Analyzing all addresses took 
us around one month.

```bash
# ~90 seconds
inline@a9cc16b080f9:~$ tail -n +2 database/contract_addresses.csv| shuf -n 50 > $TARGET/dataset.csv
inline@a9cc16b080f9:~$ cat $TARGET/dataset.csv | cut -d ',' -f1 > $TARGET/contracts.csv
```

These commands will generate two new files. `$TARGET/dataset.csv` contains 
addresses of contracts along with the number of transactions of the contract,
the number of unique callers of this contract, the number of token transfers,
its balance, a boolean value to declare if the contract is an ERC20 contract,
a boolean value to declare if the contract is an ERC721 contract, 
and its timestamp (i.e., block number).
`$TARGET/contracts.csv` simply contains only the addresses of the selected 
contracts.

3. Crawl Etherscan to get the source code of the contracts.

```bash
# ~60 seconds
inline@a9cc16b080f9:~$ python scripts/get_contracts.py --dataset $TARGET $API_KEY $TARGET/contracts.csv
Etherscan API Key      XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
Nr of contracts        50
Contracts processed    0
Dataset                sample_dataset -- 0

Addresses processed 50 / 50 ✔   Succeed             27 / 50 ✔   Empty               23 / 50 ✔   Invalid             0 / 50 ✘

Total      50
New        50
Succeed    27
Empty      23
Invalid    0
```

This script uses the API of <https://etherscan.io> and tries to download the 
verified source code of its contract if available.
For example, in the above run: 27 contracts have their code verified in 
<https://etherscan.io>, whereas 23 do not. Note that if invalid is greater than 1, 
it means that the request fails for some contracts.
That could happen, for example, if your network is unstable. 
You can re-run the exact same command
to try to query the missing contracts.

The results of this script are saved in two directories: `$TARGET/json` and `$TARGET/sol`.
The former would contain a JSON file for each contract address regardless 
if we managed to download its source code.
Each JSON contains the source code (if available), the ABI (if available), 
the version of the compiler it was used to compile the contract, 
optimization options used (if available), and some additional fields such as 
license type and EVM version.
On the other hand, in `$TARGET/sol` it saves a file per contract address, 
only for verified contracts containing their source code.

### Post Filtering

__MAC OSx users: If you run this without using docker, note that in the following 
we use gnu commands, thus; you will need to download gnu-utils 
(<https://apple.stackexchange.com/questions/69223/how-to-replace-mac-os-x-utilities-with-gnu-core-utilities>)
and use gmv and gcp instead of mv and cp.__

Note that in this section we'll use the following programs:

* `cat`
* `tr`
* `sha256sum`
* `awk`
* `sort`

Check before running the following commands that you have installed the aforementioned
tools (all of them are by default installed in most UNIX-like OSes).

You will also need to install the following tools.

* `cloc`
* `jq`

4. Set dataset file

```bash
inline@a9cc16b080f9:~$ DATASET=contracts.csv
```

5. Split files that contain multiple contracts

Some of the files in `$TARGET/sol` may be JSON files that contain multiple contracts.
You can run the following command to split those contracts into multiple files. 
The files will be created into a directory named after the initial file.

```bash
inline@a9cc16b080f9:~$ python scripts/split_mutliple_files.py ${TARGET}/sol

Find Files
Nr of files: 27
Get JSON files
100%|████████████████████████████████████████████████████████████████████████████████████████████████| 27/27 [00:00<00:00, 223.44it/s]
Filter JSON files
Nr of JSON files: 0
```

6. Get duplicates

Now we are going to find duplicate contracts.

```bash
inline@a9cc16b080f9:~$ find ${TARGET}/sol ! -empty -type f \
    -exec sh -c "cat '{}' | tr -d '[:space:]' | sha256sum | awk '{print \$1 \" {} \"}' " \;  \
    | sort > ${TARGET}/sha256sum_results
inline@a9cc16b080f9:~$ cat ${TARGET}/sha256sum_results | \
    ./scripts/create_duplicates_json.py > ${TARGET}/sha256_result.json
inline@a9cc16b080f9:~$ python scripts/process_duplicates.py ${TARGET}/sol/ \
    ${TARGET}/sha256_result.json \
    ${TARGET}/duplicates.json

Read sample_dataset/sha256_result.json
Get multi contracts and results
100%|█████████████████████████████████████████████████████████████████████████████████████████████| 27/27 [00:00<00:00, 157068.25it/s]
Get hashes for multicontract addesses
0it [00:00, ?it/s]
Write sample_dataset/duplicates.json

Total unique hashes: 4
```

This will create a file that contains a map from an address to a hash and
a map from hashes to addresses.

```
{
    "hashes": {
        "hash1": ["address1", "address2"]
    },
    "addresses": {
        "address1": "hash1"
    }
}
```

7. Find unique addresses

The following commands will create `${TARGET}/unique_addresses.txt` and
`${TARGET}/unique_paths.txt`. The first file contains the addresses of unique 
contracts, whereas the second contains their paths to the respective source
code files. We perform that step so we can analyze duplicate contracts only once.
Then, when feeding the database, we'll feed the data for all contracts using
the results of the duplicates.

```bash
inline@a9cc16b080f9:~$ cat ${TARGET}/duplicates.json | jq -r '.hashes | .[] | .[0]' \
    > ${TARGET}/unique_addresses.txt
# Create list of complete paths
inline@a9cc16b080f9:~$ cat ${TARGET}/unique_addresses.txt | \
    awk -v env_var="${TARGET}" '{ print env_var "/sol/" $0 ".sol"; }' \
    > ${TARGET}/unique_paths.txt
```

8. Get LOCs of contracts

Here we use cloc to compute the lines of code of each smart contract.

```bash
inline@a9cc16b080f9:~$ cloc --csv ${TARGET}/sol/ \
    --list-file=${TARGET}/unique_paths.txt \
    --report-file=${TARGET}/cloc_results.csv \
    --ignored=${TARGET}/cloc_ignored.csv \
    --include-lang=Solidity --by-file

       4 text files.
       4 unique files.
Wrote sample_dataset/cloc_ignored.csv
       0 files ignored.
Wrote sample_dataset/cloc_results.csv

inline@a9cc16b080f9:~$ python scripts/process_cloc_results.py \
    ${TARGET}/sol/ \
    ${TARGET}/cloc_results.csv \
    ${TARGET}/cloc_ignored.csv \
    ${TARGET}/unique_lines.csv
Read sample_dataset/cloc_results.csv
Read sample_dataset/cloc_ignored.csv
Get final results
Write sample_dataset/unique_lines.csv
```

9. Find contracts with assembly code (Optionally)

The following command will simply print how many contracts contain inline assembly.

```bash
inline@a9cc16b080f9:~$ cat ${TARGET}/unique_paths.txt \
    | xargs grep -r -l -o ".*assembly.*" | cut -d '/' -f1,2,3 | uniq | wc -l
```

10. Export contracts with assembly code

Now we'll create a directory named `assembly`, on which we are going to
copy all the unique contracts that contain inline assembly.
Note that instead of `cp` you can use `mv`.

```bash
inline@a9cc16b080f9:~$ mkdir ${TARGET}/assembly
inline@a9cc16b080f9:~$ cat ${TARGET}/unique_paths.txt \
    | xargs grep -r -l -o ".*assembly.*" | cut -d '/' -f1,2,3 | uniq \
    | xargs -I{} cp -r -u {} ${TARGET}/assembly
```

### Source Code Analysis

11. Process Contracts

First, we are going to use a custom parser that detects and analyzes 
inline assembly fragments. In the following command, you can replace
`4` with the number of cores you want to use.

```bash
# ~5-10 seconds depending on how many contracts you have to analyze
inline@a9cc16b080f9:~$ ./scripts/run_parser.sh ${TARGET}/assembly ${TARGET}/parser 4
```

This will create a directory called `${TARGET}/parser` that contains JSON files 
with the analysis results.

12. Create a list with contracts that contain assembly.

The following commands will produce two new files:
`$TARGET/assembly_contracts.csv` and `$TARGET/non_assembly_contracts.csv`.
The former contains all addresses of contracts that contain at least one
inline assembly fragment, whereas the latter contains all addresses of contracts
that do not contain inline assembly.

```bash
inline@a9cc16b080f9:~$ python scripts/contains_assembly.py \
    ${TARGET}/parser \
    ${TARGET}/duplicates.json \
    > ${TARGET}/assembly_contracts.csv
inline@a9cc16b080f9:~$ comm -23 <(ls ${TARGET}/sol | sed 's/\.sol//g' | sort) \
    <(sort ${TARGET}/assembly_contracts.csv) \
    > ${TARGET}/non_assembly_contracts.csv
```

### Feed Results into the Database

Here we will first create a JSON file with some data we have already gathered
from etherscan (i.e., `CompilerVersion` and `EVMVersion`), then we'll 
create CSV files for each table of the database schema. Next, we'll initialize
the database, and finally, we'll feed the data into the database.

13. Create JSON file with Etherscan data.

```bash
inline@a9cc16b080f9:~$ python scripts/get_etherscan.py ${TARGET}/json ${TARGET}/etherscan_data.json
Read sample_dataset/json
Process sample_dataset/json
100%|████████████████████████████████████████████████████████████████████████████████████████████████| 50/50 [00:00<00:00, 379.05it/s]
Write sample_dataset/etherscan_data.json
```

14. Create CSV Files to Populate the Database

This script takes as input all the files we have generated in the previous steps
(i.e., `dataset.csv`, `unique_lines.csv`, `duplicates.json`, 
`etherscan_data.json`, `parser`), and it generates a CSV file per table of 
our database schema into the `$TARGET/csvs` directory.

```bash
inline@a9cc16b080f9:~$ python scripts/create_csv.py \
    $TARGET/dataset.csv \
    ${TARGET}/unique_lines.csv \
    ${TARGET}/duplicates.json \
    ${TARGET}/etherscan_data.json \
    ${TARGET}/parser \
    ${TARGET}/csvs \
    --labels data/labels.json 
Read LOC
Read Duplicates
Read etherscan data
Read Address Metadata
50it [00:00, 110901.75it/s]
Process results (duplicates)
100%|██████████████████████████████████████████████████████████████████████████████████████████████████| 4/4 [00:00<00:00, 822.53it/s]
Process Labels
Save results
```

15. Create and populate the database

The following commands will first generate an SQLite database, and then it 
will feed the results of the analysis into the database.

```bash
inline@a9cc16b080f9:~$ ./scripts/create_db.sh ${TARGET}/db inline.db scripts/schema.sql
-- Loading resources from scripts/schema.sql
# We redirect stderr to /dev/null because Opcode.csv and OldOpcode.csv 
# contain, on purpuse, some lines that break the unique contraint check.
inline@a9cc16b080f9:~$ sqlite3 $TARGET/db/inline.db < ${TARGET}/csvs/populate.sql 2> /dev/null
```

To check if the database has been initialized, you can run the following
command.

```bash
inline@a9cc16b080f9:~$ sqlite3 $TARGET/db/inline.db "SELECT count(*) FROM Address"
5
```

### Print Results

16. Print Statistics of the Dataset

```bash
inline@a9cc16b080f9:~$ TOTAL=$(cat $TARGET/contracts.csv | wc -l | xargs)
inline@a9cc16b080f9:~$ python scripts/db_queries.py ${TARGET}/db/inline.db --total-contracts $TOTAL
Source statistics
-----------------

Total addresses processed: 50
Solidity source not available: 23 (46%)
Solidity source available: 27 (54%)
LOC: 2165
Unique Solidity Contracts: 6 (22%)
LOC of Unique Solidity Contracts: 514
```

17. Print the Results of the Quantitative Analysis

```bash
# Probably it will print in the end an error message that it can't generate
# figures/taxonomy_categories.pdf because there aren't enough data.
inline@a9cc16b080f9:~$ python scripts/db_queries.py ${TARGET}/db/inline.db --quantitative-analysis
...
```

For more details about the quantitative analysis, refer to the respective
[section](#quantitatively-study-inline-assembly-on-solidity-smart-contracts-section4#).

## Analyze Single Smart Contract for Inline Assembly Fragments

### Dependencies

First, you need to install [solidity-parser](https://pypi.org/project/solidity-parser/) PyPI package.

```bash
pip install solidity-parser
```

### Usage

```bash
python scripts/analyze_contracts.py -h
usage: analyze_contracts.py [-h] [-p] [-s SAVE] [-c] file

Process inline assembly of a solidity file

positional arguments:
  file                  Path of the solidity file or directory with solidity files

optional arguments:
  -h, --help            show this help message and exit
  -p, --print           Print statistics
  -s SAVE, --save SAVE  Save results to JSON
  -c, --code            Save Code
```

### Example: Analyze a smart contract

```bash
python scripts/analyze_contracts.py tests/large.sol -p
Processing file: tests/large.sol
Number of contracts: 1
Number of functions: 45
Number of lines: 1769

Number of contracts with assembly: 1
Number of functions with assembly : 45
Number of assembly lines: 1387
Number of assembly fragments: 49

Top OPCODES: add (312), mstore (224), sload (134), revert (129), and (116)
Top HIGH_LEVEL_CONSTRUCTS: if (136), switch (6), for (6)
Top DECLARATIONS: let (298)
```
