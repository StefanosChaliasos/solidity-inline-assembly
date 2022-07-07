Download the Database
=====================

__NOTE:__ The total size of the downloaded files after extracting them is
5.5G.

This file contains the instructions for downloading the SQLite database used to 
perform the quantitative analysis presented in the paper. 
You can find the database at this link
<https://zenodo.org/record/6801913>.
To download the tarball that contains the database and a file with all
the contract addresses, run the following commands.

```bash
# With an average internet connection that could take up to 15 minutes.
curl -o database-solidity-inline-assembly.tar.gz \
    https://zenodo.org/record/6801913/files/database-solidity-inline-assembly.tar.gz\?download\=1
tar xvf database-solidity-inline-assembly.tar.gz
```

These commands will download `database-solidity-inline-assembly.tar.gz` and then
extract it to the `database` directory. This directory contains 
`inline.db`, the database used for the quantitative analysis, and 
`contract_addresses.csv` a file with all the addresses of contracts with
at least one transaction or a token transfer.
