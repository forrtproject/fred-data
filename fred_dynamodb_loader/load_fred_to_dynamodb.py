#!/usr/bin/env python3
"""
FReD → DynamoDB ETL (preserve CSV columns; parse JSON-looking cells)

- Keeps all CSV columns exactly as named (no renaming),
  EXCEPT drops: url_r, ref_r, ref_o, bibtex_ref_r.
- For each cell:
    * NaN/NA  -> None
    * If starts with '{' or '[' -> try json.loads -> keep dict/list if valid
    * else keep as-is (string/number/bool)
- Groups rows by 3-char original DOI hash (doi_o_hash[:PREFIX_LEN]).
- Writes TWO tables:
    1) PREFIX table:  PK 'prefix' -> 'candidates' (JSON string)
       candidates = [ { hash_prefix, meta: { original_doi, replications:[ <row dicts> ] } }, ... ]
    2) ORIGINAL table: PK 'original_doi' -> { prefix, candidate } (JSON string)
       candidate = { hash_prefix, meta: { original_doi, replications:[ <row dicts> ] } }

Env:
  TABLE            DynamoDB prefix table name (required)
  ORIGINAL_TABLE   DynamoDB original table name (optional; derived if TABLE endswith -prefix)
  AWS_REGION       AWS region (default: eu-central-1)
  PREFIX_COL       Name of the hash column (default: doi_o_hash)
  PREFIX_LEN       How many chars to use from hash (default: 3)

Usage:
  python etl/build_from_csv_allcols.py /path/to/fred.csv
"""
import os, sys, json
from collections import defaultdict
import boto3
import pandas as pd
import html

TABLE          = os.getenv("TABLE")
AWS_REGION     = os.getenv("AWS_REGION", "eu-central-1")
PREFIX_COL     = os.getenv("PREFIX_COL", "doi_o_hash")
PREFIX_LEN     = int(os.getenv("PREFIX_LEN", "3"))
ORIGINAL_TABLE = os.getenv("ORIGINAL_TABLE")

REQUIRED_COLS = {PREFIX_COL, "doi_o"}     # need hash + original DOI
DROP_COLS = { "ref_o"}

if not TABLE:
    print("ERROR: set TABLE env var", file=sys.stderr); sys.exit(1)
if not ORIGINAL_TABLE:
    if TABLE.endswith("-prefix"):
        ORIGINAL_TABLE = TABLE[:-len("-prefix")] + "-original"
    else:
        print("ERROR: set ORIGINAL_TABLE (or name TABLE like ...-prefix)", file=sys.stderr)
        sys.exit(1)

from ftfy import fix_text
import html
import json
import pandas as pd
from ftfy import fix_text

def to_jsonable(value):
    """
    Cleans and converts a single cell value for JSON storage:
      - NaN / NA -> None
      - Decodes HTML entities (&amp; -> &)
      - Fixes encoding errors (mojibake like √± -> ñ)
      - Parses JSON-looking strings ({...} or [...]) safely
      - Returns clean string / number / bool / None
    """
    if pd.isna(value):
        return None

    if isinstance(value, str):
        # Trim and clean
        s = value.strip()

        # Step 1: Decode HTML entities
        s = html.unescape(s)

        # Step 2: Fix encoding issues (mojibake)
        s = fix_text(s)

        # Step 3: Parse JSON-like strings if valid
        if s.startswith("{") or s.startswith("["):
            try:
                return json.loads(s)
            except Exception:
                return s  # not valid JSON, return as-is

        return s  # normal string, cleaned
    else:
        # numbers / booleans stay as-is
        return value


def clear_table(table):
    """Delete all items from a DynamoDB table (scans in batches)."""
    import boto3
    from boto3.dynamodb.conditions import Key

    ddb = boto3.resource("dynamodb", region_name=AWS_REGION)
    tbl = ddb.Table(table)
    print(f"Clearing table: {table}")

    # Scan to get keys (careful: scans can be slow for large tables)
    key_schema = [k["AttributeName"] for k in tbl.key_schema]

    scan_kwargs = {}
    done = False
    start_key = None
    count = 0

    while not done:
        if start_key:
            scan_kwargs["ExclusiveStartKey"] = start_key
        response = tbl.scan(**scan_kwargs)
        items = response.get("Items", [])
        if not items:
            break

        with tbl.batch_writer() as batch:
            for item in items:
                key = {k: item[k] for k in key_schema}
                batch.delete_item(Key=key)
                count += 1

        start_key = response.get("LastEvaluatedKey", None)
        done = start_key is None

    print(f"Deleted {count} items from {table}.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python etl/build_from_csv_allcols.py /path/to/fred.csv", file=sys.stderr)
        sys.exit(2)
    csv_path = sys.argv[1]
    if not os.path.exists(csv_path):
        print(f"ERROR: file not found: {csv_path}", file=sys.stderr); sys.exit(3)

    print(f"Reading CSV: {csv_path}")
    df = pd.read_csv(csv_path, encoding="utf-8", engine="python", on_bad_lines="warn")

    # verify required columns exist (case-insensitive)
    cols_lower = {c.lower(): c for c in df.columns}
    missing = [c for c in REQUIRED_COLS if c.lower() not in cols_lower]
    if missing:
        print(f"ERROR: missing required columns: {missing}", file=sys.stderr)
        print(f"Found columns: {list(df.columns)}", file=sys.stderr)
        sys.exit(4)

    col = lambda name: cols_lower[name.lower()]
    prefix_col = col(PREFIX_COL)
    doi_o_col  = col("doi_o")

    # columns to keep (as-named), excluding the four drops
    drop_lower = {d.lower() for d in DROP_COLS}
    keep_cols = [c for c in df.columns if c.lower() not in drop_lower]

    # index: prefix -> (original_doi -> candidate)
    index: dict[str, dict[str, dict]] = defaultdict(dict)

    for _, row in df.iterrows():
        raw_prefix = row.get(prefix_col)
        if pd.isna(raw_prefix): continue
        prefix = str(raw_prefix).strip()[:PREFIX_LEN]
        if not prefix: continue

        od_val = row.get(doi_o_col)
        if pd.isna(od_val): continue
        original_doi = str(od_val).strip()
        if not original_doi: continue

        # Build replication dict using ALL kept columns (names preserved)
        rep_dict = {}
        for c in keep_cols:
            rep_dict[c] = to_jsonable(row[c])

        # One candidate per ORIGINAL DOI within this prefix
        cand = index[prefix].get(original_doi)
        if not cand:
            cand = {
                "hash_prefix": prefix,
                "meta": {
                    "original_doi": original_doi,
                    "replications": []
                }
            }
            index[prefix][original_doi] = cand

        # Optional de-dupe: if there is a 'doi_r' column, avoid dup DOIs
        doi_r_val = rep_dict.get("doi_r")
        reps = cand["meta"]["replications"]
        if doi_r_val is not None:
            if not any(e.get("doi_r") == doi_r_val for e in reps):
                reps.append(rep_dict)
        else:
            reps.append(rep_dict)

    # Flatten for PREFIX table
    prefix_items = []
    for prefix, originals_map in index.items():
        candidates = list(originals_map.values())
        prefix_items.append({"prefix": prefix, "candidates": candidates})

    print(f"Prepared {len(prefix_items)} prefix items.")

    # DynamoDB writes
    ddb = boto3.resource("dynamodb", region_name=AWS_REGION)
    prefix_table = ddb.Table(TABLE)
    original_table = ddb.Table(ORIGINAL_TABLE)
    # Clear both tables before writing
    clear_table(TABLE)
    clear_table(ORIGINAL_TABLE)

    # 1) PREFIX table (store candidates as a single JSON string)
    with prefix_table.batch_writer(overwrite_by_pkeys=["prefix"]) as batch:
        for item in prefix_items:
            batch.put_item(Item={
                "prefix": item["prefix"],
                "candidates": json.dumps(item["candidates"], ensure_ascii=False)
            })

    # 2) ORIGINAL table (one item per ORIGINAL DOI)
    original_rows = []
    for itm in prefix_items:
        pfx = itm["prefix"]
        for cand in itm["candidates"]:
            od = cand.get("meta", {}).get("original_doi")
            if not od: continue
            original_rows.append({
                "original_doi": od,
                "prefix": pfx,
                "candidate": cand
            })

    with original_table.batch_writer(overwrite_by_pkeys=["original_doi"]) as batch:
        for row in original_rows:
            batch.put_item(Item={
                "original_doi": row["original_doi"],
                "prefix": row["prefix"],
                "candidate": json.dumps(row["candidate"], ensure_ascii=False)
            })

    print(f"Wrote {len(prefix_items)} prefix items and {len(original_rows)} original items.")
    print("Done.")

if __name__ == "__main__":
    main()
