#!/bin/bash
#
# Query base:
#SELECT COUNT(f.fragment_id)
#FROM Address AS a
#JOIN SolidityFile AS s ON a.address_id = s.address_id
#JOIN Contract AS c ON s.file_id = c.file_id
#JOIN Fragment AS f ON c.contract_id = f.contract_id
#WHERE a.nr_transactions = 0 AND a.nr_token_transfers = 0;

DB=$1


# Delete Instructions
echo "$(date): Deleting HighLevelConstructsPerFragment"
sqlite3 $DB "DELETE FROM HighLevelConstructsPerFragment WHERE fragment_id IN (SELECT f.fragment_id FROM Address AS a JOIN SolidityFile AS s ON a.address_id = s.address_id JOIN Contract AS c ON s.file_id = c.file_id JOIN Fragment AS f ON c.contract_id = f.contract_id WHERE a.nr_transactions = 0 AND a.nr_token_transfers = 0);"
echo "$(date): Deleting DeclarationsPerFragment"
sqlite3 $DB "DELETE FROM DeclarationsPerFragment WHERE fragment_id IN (SELECT f.fragment_id FROM Address AS a JOIN SolidityFile AS s ON a.address_id = s.address_id JOIN Contract AS c ON s.file_id = c.file_id JOIN Fragment AS f ON c.contract_id = f.contract_id WHERE a.nr_transactions = 0 AND a.nr_token_transfers = 0);"
echo "$(date): Deleting SpecialOpcodesPerFragment"
sqlite3 $DB "DELETE FROM SpecialOpcodesPerFragment WHERE fragment_id IN (SELECT f.fragment_id FROM Address AS a JOIN SolidityFile AS s ON a.address_id = s.address_id JOIN Contract AS c ON s.file_id = c.file_id JOIN Fragment AS f ON c.contract_id = f.contract_id WHERE a.nr_transactions = 0 AND a.nr_token_transfers = 0);"
echo "$(date): Deleting OldOpcodesPerFragment"
sqlite3 $DB "DELETE FROM OldOpcodesPerFragment WHERE fragment_id IN (SELECT f.fragment_id FROM Address AS a JOIN SolidityFile AS s ON a.address_id = s.address_id JOIN Contract AS c ON s.file_id = c.file_id JOIN Fragment AS f ON c.contract_id = f.contract_id WHERE a.nr_transactions = 0 AND a.nr_token_transfers = 0);"
echo "$(date): Deleting OpcodesPerFragment"
sqlite3 $DB "DELETE FROM OpcodesPerFragment WHERE fragment_id IN (SELECT f.fragment_id FROM Address AS a JOIN SolidityFile AS s ON a.address_id = s.address_id JOIN Contract AS c ON s.file_id = c.file_id JOIN Fragment AS f ON c.contract_id = f.contract_id WHERE a.nr_transactions = 0 AND a.nr_token_transfers = 0);"

echo "$(date): Deleting Fragment"
sqlite3 $DB "DELETE FROM Fragment WHERE contract_id IN (SELECT c.contract_id FROM Address AS a JOIN SolidityFile AS s ON a.address_id = s.address_id JOIN Contract AS c ON s.file_id = c.file_id WHERE a.nr_transactions = 0 AND a.nr_token_transfers = 0);"

echo "$(date): Deleting Contract"
sqlite3 $DB "DELETE FROM Contract WHERE file_id IN (SELECT s.file_id FROM Address AS a JOIN SolidityFile AS s ON a.address_id = s.address_id WHERE a.nr_transactions = 0 AND a.nr_token_transfers = 0);"

echo "$(date): Deleting SolidityFile"
sqlite3 $DB "DELETE FROM SolidityFile WHERE address_id IN (SELECT a.address_id FROM Address AS a WHERE a.nr_transactions = 0 AND a.nr_token_transfers = 0);"

echo "$(date): Deleting Address"
sqlite3 $DB "DELETE FROM Address WHERE nr_transactions = 0 AND nr_token_transfers = 0;"

echo "$(date): Deleting NonAssemblyAddress"
sqlite3 $DB "DELETE FROM NonAssemblyAddress WHERE nr_transactions = 0 AND nr_token_transfers = 0;"

echo "$(date): Finished"
