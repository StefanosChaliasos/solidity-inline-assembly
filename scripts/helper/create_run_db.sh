#!/bin/bash
# Utility script that runs the following scripts:
# 1. create_csv.py
# 2. create_db.sh
# 3. sqlite3 to populate
# 4. db_queries.py
if [ $# -lt 1 ]; then
    echo $0: usage: create_run_db.sh target 
    exit 1
fi

TARGET=$1

echo "Generate CSVs" && \
    python scripts/create_csv.py ${TARGET}/parser \
        ${TARGET}/parser.json \
        ${TARGET}/csvs \
        --non-assembly ${TARGET}/without_assembly.json \
        --labels data/labels.json && \
    echo "Create DB" && \
    ./scripts/create_db.sh ${TARGET}/db inline.db scripts/schema.sql && \
    echo "Populate DB" && \
    sqlite3 ${TARGET}/db/inline.db < ${TARGET}/csvs/populate.sql && \
    echo "Run queries" && \
    python scripts/db_queries.py ${TARGET}/db/inline.db --print-rqs
