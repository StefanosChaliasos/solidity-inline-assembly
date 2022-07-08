#!/bin/bash

if [ $# -lt 3 ]; then
    echo $0: usage: run_parser.sh input_directory output_directory processes
    exit 1
fi

INPUT_DIR=$1
OUTPUT_DIR=$2
N=$3

mkdir -p $OUTPUT_DIR

task(){
    i=$1
    without_ext="${i%.*}"
    f=$INPUT_DIR/$i
    filename=$OUTPUT_DIR/$(basename $f)
    out="${filename%.*}".json

    if [[ -f "$out" ]]; then
        echo "skip: $out"
        continue
    elif [[ ! -f "$f" ]] && [[ ! -d "$f" ]]; then
        echo "error: $f does not exist"
        continue
    else
        python scripts/analyze_contracts.py -s $out $f
    fi

}

for fpath in $(ls $INPUT_DIR); do
    ((i=i%N)); ((i++==0)) && wait
    task $fpath &
done

# We need that just to prevent printing prompt before everything has finished.
sleep 5
echo "Finished"
