"""
Process the results of cloc and save them in a CSV file.
"""
import argparse
import csv

from collections import defaultdict


def get_args():
    args = argparse.ArgumentParser(
        "Process cloc result"
    )
    args.add_argument("path", help="Dataset filepath")
    args.add_argument("results", help="CSV output of cloc")
    args.add_argument("ignored", help="Files ignored by cloc")
    args.add_argument("output", help="Output file to save the results")
    return args.parse_args()


def main():
    args = get_args()

    cloc_results = {}
    results = defaultdict(lambda: 0)
    number_of_slashes = args.path.count('/')

    print(f"Read {args.results}")
    with open(args.results, 'r') as fp:
        reader = csv.reader(fp, delimiter=",", quotechar='"')
        # Skip headers
        next(reader)
        cloc_results = {row[1]: int(row[4]) for row in reader}
        if '' in cloc_results:
            del cloc_results['']  # This line contains the SUM

    print(f"Read {args.ignored}")
    with open(args.ignored, 'r') as fp:
        reader = csv.reader(fp, delimiter=",", quotechar='"')
        for row in reader:
            if len(row) == 0:
                continue
            # Different versions of cloc have different delimiters
            if ':' in row[0]:
                row = row[0].split(':')
            path = row[0]
            if len(row) <= 1 or "duplicate of " not in row[1]:
                print(f"Warning: {path} was ignored for an unknown reason")
                continue
            duplicated = row[1].replace('duplicate of ', '').strip()
            cloc_results[path] = cloc_results[duplicated]

    print("Get final results")
    for path, value in cloc_results.items():
        if path.count('/') == number_of_slashes:
            results[path] += int(value)
        else:
            original_path = "/".join(path.split('/')[:number_of_slashes+1])
            results[original_path] += int(value)

    rows = [[path,value] for path, value in results.items()]

    print(f"Write {args.output}")
    with open(args.output, 'w') as fp:
        writer = csv.writer(fp, delimiter=",")
        writer.writerows(rows)


if __name__ == "__main__":
    main()
