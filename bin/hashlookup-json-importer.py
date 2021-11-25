import hashlookup.hashlookup as hashlookup
import argparse
import sys
from glob import glob
import os
import json

BUF_SIZE = 65536

parser = argparse.ArgumentParser(description="Generic NDJSON importer for hashlookup server")
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output", default=False)
parser.add_argument(
    "-s", "--source", help="Source name to be used as meta", default="hashlookup-json-import"
)
parser.add_argument("-p", "--parent", help="Parent SHA-1 of the import", default=None)
parser.add_argument(
    "--parent-meta",
    help="Add metadata to parent, format is key,value",
    default=None,
    nargs='+',
)
parser.add_argument(
    "-u",
    "--update",
    help="Update hash if it already exists. default is to update existing hashlookup record without deleting existing.",
    action="store_true",
    default=True,
)
parser.add_argument(
    "-e",
    "--skip-exists",
    action="store_true",
    default=False,
    help="Skip import of existing hashlookup record",
)

args = parser.parse_args()


if not args.update:
    h = hashlookup.HashLookupInsert(
        update=False, source=args.source, skipexists=args.skip_exists, publish=True
    )
else:
    h = hashlookup.HashLookupInsert(
        update=True, source=args.source, skipexists=args.skip_exists, publish=True
    )

if args.verbose:
    v = h.get_version()
    print(f"hashlookup-lib version: {v}")
    
hashes = ['md5', 'sha-1', 'sha-256', 'sha-512', 'tlsh', 'ssdeep']    
for line in sys.stdin:
    record = json.loads(line)
    for key in record.keys():
        if key.lower() in hashes:
            k = key.upper()
            if record[key] == "":
                continue
            h.add_hash(value=record[key], hashtype=k)
            continue
        h.add_meta(key=key, value=record[key])
    if args.parent is not None:
        h.add_parent(value=args.parent)
    if (args.parent and args.parent_meta) is not None:
        for pmeta in args.parent_meta:
            k, v = pmeta.split(",")
            h.add_parent_meta(value=args.parent, meta_key=k, meta_value=v)
    r = h.insert()
    if args.verbose:
        print(f"Imported -> {r}")
