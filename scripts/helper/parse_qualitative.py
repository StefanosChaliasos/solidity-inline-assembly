import argparse
import json

from collections import defaultdict


def get_args():
    args = argparse.ArgumentParser(
        "Process qualitative analysis resutls"
    )
    args.add_argument("path", help="Qualitative analysis filepath")
    return args.parse_args()


def main():
    args = get_args()
    results = defaultdict(list)

    with open(args.path, 'r') as fp:
        lines = fp.readlines()
        for line in lines:
            if line.startswith('Number'):
                fid = line.replace('Number', '').strip()
            if line.startswith('Category:'):
                categories = line.replace('Category:', '').strip().split(',')
                for category in categories:
                    category = category.strip()
                    results[category].append(fid)
    for category, ids in sorted(results.items()):
        print(f"{category}: {len(ids)}")
        print(ids)



if __name__ == "__main__":
    main()
