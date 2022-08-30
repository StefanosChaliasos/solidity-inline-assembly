Patch the database
==================

In the database, there are some additional entries that should not exist.
More specifically, there are two kinds of entries that we should remove.

1. Cases where the source code of an address was downloaded and saved in the
filesystem with caps by the Etherscan API. In such cases, because we rerun the
`get_contracts.py` script, we eventually downloaded the source code with the
correct address hash (all lowercase). Nevertheless, due to a
[bug](https://github.com/StefanosChaliasos/solidity-inline-assembly/blob/28e64dcc968b0b26a6f5a544656d72f4a0e6d9a0/scripts/create_csv.py#L116)
in the `create_db.py` script, we saved both entries in the database.
To solve that, we simply need to remove the duplicated addresses from the database.
2. Contract addresses without a token transfer or a transaction are added to the database.
This happens because in one of the machines, we have started to crawl all
contracts, and we did not remove those addresses from the dataset retrieved in
that machine before merging everything to a single dataset.
Again, we will just remove those addresses directly from the database.


* Delete all superfluous data from the database.

```
# This would take around 30 seconds
./delete.sh ../database/inline.db
```

