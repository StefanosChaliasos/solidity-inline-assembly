#!/bin/bash
# Initialize a database for inline assembly fragments

if [ $# -lt 2 ]; then
    echo $0: usage: create_db.sh destination db_name schema
    exit 1
fi

DESTINATION=$1
NAME=$2
DB=$DESTINATION/$NAME
SCHEMA=$3

mkdir -p $DESTINATION
rm -rf $DB
sqlite3 -init $SCHEMA $DB .quit
