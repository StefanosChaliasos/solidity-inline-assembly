Download the Dataset
====================

__NOTE:__ The total size of the downloaded files after extracting them is
162G.

__NOTE:__ This dataset is not required to verify the artifact for the OOPSLA
paper. The dataset is provided to help researchers do more empirical studies
in Solidity Smart contracts beyond analyzing inline assembly usage.

This file contains the instructions for downloading the dataset composed
for analyzing the usage of inline assembly in Solidity smart contracts 
deployed in the Ethereum mainet.
You can find the dataset in this link
<https://zenodo.org/record/6807660>.
To download the tarball that contains the dataset, run the following commands.

```bash
# With an average internet connection that could take up to XXX minutes.
curl -o database-solidity-inline-assembly.tar.gz \
    https://zenodo.org/record/6807660/files/dataset-solidity-inline-assembly.tar.gz\?download\=1
tar xvf dataset-solidity-inline-assembly.tar.gz
```

These commands will download `dataset-solidity-inline-assembly.tar.gz` and then
extract it to the `dataset` directory. This directory contains the following
files and directories.

* `dataset.csv`: A CSV file with all the addresses of contracts with at least
one transaction or a token transfer, along with the number of transactions of 
the contract, the number of unique callers of this contract, the number of 
token transfers, its balance, a boolean value to declare if the contract is 
an ERC20 contract, a boolean value to declare if the contract is an ERC721 
contract, and its timestamp (i.e., block number).
* `contracts.csv`: A file with all the addresses of contracts with at least
one transaction or a token transfer.
* `json{1..2}/`: These directories contain a JSON file for each contract 
address regardless of if its source code is available. 
Each JSON contains the source code (if available), the ABI 
(if available), the version of the compiler it was used to compile the 
contract, optimization options used (if available), and some additional 
fields such as license type and EVM version.
Note that there are two directories because it is not possible to save
all files into a single directory.
* `sol/`: The source code for all contracts that have their code verified in
<https://etherscan.io>. If there are multiple source files compiled into one
smart contract, then we create a directory with the name of the address, and we
save the files into this directory. Otherwise; we directly save the smart
contract in a filename named after the address.
* `duplicates.json`: A map from an address to a hash and a map from hashes to
addresses.

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

* `unique_addresses.txt`: A file that contains all unique addresses.
* `unique_paths.txt`: A file that contains the paths for all unique addresses.
* `unique_lines.csv`: A CSV file that contains unique paths and their LOC.
* `assembly/`: A directory with all the addresses that could potentially include 
inline assembly fragments. Note that this directory could contain false 
positives as the work `assembly` could exist only in the comments. In a later
stage, using a static analysis tool, we eliminate those false positives.
* `parser/`: This directory contains JSON files with the analysis results for
all contracts in the `assembly/` directory.
