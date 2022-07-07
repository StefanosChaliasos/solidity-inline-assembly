#!/bin/bash
# Get the first 7 lines of Figure 3

if [ $# -lt 1 ]; then
    echo $0: usage: get_statistics.sh contracts.csv
    exit 1
fi

CONTRACTS=$1
WITHOUT_HEADER=$(cat ${CONTRACTS} | tail +2)
BLOCKS=$(echo "${WITHOUT_HEADER}" | cut -d ',' -f8)
SORTED_BLOCKS=$(echo "$BLOCKS" | sort -n)
START_BLOCK=$(echo "${SORTED_BLOCKS}" | head -1)

echo "------------------------------------------------------------------------"
echo "Start Block: ${START_BLOCK}"

END_BLOCK=$(echo "${SORTED_BLOCKS}" | tail -1)

echo "End Block: ${END_BLOCK}"
echo "------------------------------------------------------------------------"

TRANSACTIONS=$(echo "${WITHOUT_HEADER}" | cut -d "," -f2)
WITH_TRANSACTIONS=$(echo "$TRANSACTIONS" | sed '/^$/d' | wc -l | xargs)

echo "Contracts with at least one transaction: ${WITH_TRANSACTIONS}"

TOKENS=$(echo "${WITHOUT_HEADER}" | cut -d "," -f4)
WITH_TOKENS=$(echo "$TOKENS" | sed '/^$/d' | wc -l | xargs)

echo "Contracts with at least one token transfer: ${WITH_TOKENS}"

TOTAL=$(echo "${WITHOUT_HEADER}" | wc -l | xargs)

echo "Contracts with at least one transaction or token transfer: ${TOTAL}"
echo "------------------------------------------------------------------------"
