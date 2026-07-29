#!/usr/bin/env python3
"""
FReD CSV → DynamoDB (2 tables, DOI-centric record + reproduction support) — FINAL

Input CSV compatibility:
- Uses column name: "type"
- Keeps output key: "type" inside replications[] / reproductions[] entries

Key behavior:
1) Read replication/reproduction type from CSV column "type"

2) Reproduction-only rows (no doi_r) are deduped using an in-memory
   fingerprint set per doi_o. No "_id" is stored.

3) Replication-only rows (no doi_r) are also stored in record.replications[]
   and deduped using an in-memory fingerprint set per doi_o. No "_id" is stored.

4) Builds a precomputed SEARCH_TABLE for fuzzy search:
   - meta item stores total chunk count
   - chunk items "0", "1", ... store compact entries

5) Adds top-level DOI roles in "types":
   - "original"
   - "replication"
   - "reproduction"
   A DOI may have one, two, or all three roles.

Tables written:
  1) PREFIX_TABLE: prefix (3-char) -> dois (List[str])
  2) DOI_TABLE: doi (str) -> record (JSON string)
  3) SEARCH_TABLE: chunk_id (str) -> data (JSON string)

Env:
  PREFIX_TABLE       required
  DOI_TABLE          required
  SEARCH_TABLE       required
  AWS_REGION         default eu-central-1
  PREFIX_LEN         default 3
  SEARCH_CHUNK_SIZE  default 1000
  CLEAR_TABLES       default "1"

Usage:
  python etl/build_two_tables_doi_records.py <csv_file>
"""

import os
import sys
import json
import html
import hashlib
from collections import defaultdict

import boto3
import pandas as pd
from ftfy import fix_text

AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
PREFIX_TABLE = os.getenv("PREFIX_TABLE")
DOI_TABLE = os.getenv("DOI_TABLE")
SEARCH_TABLE = os.getenv("SEARCH_TABLE")
PREFIX_LEN = int(os.getenv("PREFIX_LEN", "3"))
CLEAR_TABLES = os.getenv("CLEAR_TABLES", "1").strip() not in (
    "0", "false", "False", "no", "NO"
)
SEARCH_CHUNK = int(os.getenv("SEARCH_CHUNK_SIZE", "500"))

if not PREFIX_TABLE or not DOI_TABLE or not SEARCH_TABLE:
    print(
        "ERROR: set PREFIX_TABLE, DOI_TABLE, and SEARCH_TABLE env vars",
        file=sys.stderr,
    )
    sys.exit(1)


# -----------------------------
# Core helpers
# -----------------------------

def has_col(df_or_row, col: str) -> bool:
    try:
        return col in df_or_row.index
    except Exception:
        return False


def normalize_doi(raw) -> str:
    """Normalize DOI to canonical string for keys + dedupe."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return ""
    s = str(raw).strip().lower()
    for p in (
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
    ):
        s = s.replace(p, "")
    return s.strip()


def to_jsonable(v):
    """
    Parse JSON-looking cells; decode HTML entities; fix mojibake.
    If a string starts with '{' or '[' we try json.loads to preserve nested JSON.
    """
    if v is None:
        return None
    if isinstance(v, float) and pd.isna(v):
        return None
    if isinstance(v, str):
        s = fix_text(html.unescape(v.strip()))
        if not s:
            return None
        if s.startswith("{") or s.startswith("["):
            try:
                return json.loads(s)
            except Exception:
                return s
        return s
    return v


def to_str_or_none(v):
    """Force to string or None (used for volume/issue/pages which can be numeric)."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = str(v).strip()
    return s if s else None


def norm_rep_type(v) -> str:
    """Normalized rep_type string."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return str(v).strip().lower()


def is_reproduction_type(rep_type: str) -> bool:
    """Accepts: 'reproduction', 'computational reproduction', etc."""
    rt = (rep_type or "").strip().lower()
    return rt.startswith("reproduction")


def stable_id_from_fields(*parts: str) -> str:
    """Short stable hash used ONLY for dedupe in-memory (NOT stored in output)."""
    blob = "||".join([(p or "").strip().lower() for p in parts])
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:16]


def set_if_missing(obj: dict, key: str, val):
    """Only set if currently missing/empty."""
    if val is None or val == "" or val == [] or val == {}:
        return
    cur = obj.get(key)
    if cur is None or cur == "" or cur == [] or cur == {}:
        obj[key] = val


# -----------------------------
# Record construction
# -----------------------------

def get_or_create(store: dict, doi: str):
    """Create the top-level DOI metadata + record container."""
    if doi not in store:
        store[doi] = {
            "doi": doi,

            # Top-level DOI roles
            "types": [],

            # DOI metadata (top-level)
            "doi_hash": None,
            "title": None,
            "authors": None,
            "journal": None,
            "year": None,
            "volume": None,
            "issue": None,
            "pages": None,
            "apa_ref": None,
            "bibtex_ref": None,
            "url": None,

            # Relationships + stats
            "record": {
                "stats": {
                    "n_replications_total": 0,
                    "n_replications_with_doi": 0,
                    "n_replications_only": 0,
                    "n_unique_replication_dois": 0,

                    "n_reproductions_total": 0,
                    "n_reproductions_with_doi": 0,
                    "n_reproductions_only": 0,

                    "n_originals_total": 0,
                    "n_unique_original_dois": 0,
                },
                "replications": [],
                "originals": [],
                "reproductions": [],
            },
        }
    return store[doi]


def build_original_entry(row: pd.Series) -> dict:
    """Original citation object stored inside record.originals[]."""
    out = {}
    mapping = {
        "doi": "doi_o",
        "doi_hash": "doi_o_hash",
        "title": "title_o",
        "authors": "author_o",
        "journal": "journal_o",
        "year": "year_o",
        "volume": "volume_o",
        "issue": "issue_o",
        "pages": "pages_o",
        "apa_ref": "apa_ref_o",
        "bibtex_ref": "bibtex_ref_o",
    }
    for k, col in mapping.items():
        if has_col(row, col):
            out[k] = to_jsonable(row.get(col))

    if out.get("doi"):
        out["doi"] = normalize_doi(out["doi"])
    if out.get("doi_hash") is not None:
        out["doi_hash"] = str(out["doi_hash"]).strip().lower()

    for k in ("volume", "issue", "pages"):
        if k in out:
            out[k] = to_str_or_none(out[k])

    return out


def build_replication_entry(row: pd.Series) -> dict:
    """Replication citation object stored inside record.replications[]."""
    out = {}
    mapping = {
        "doi": "doi_r",
        "doi_hash": "doi_r_hash",
        "type": "type",
        "title": "title_r",
        "authors": "author_r",
        "journal": "journal_r",
        "year": "year_r",
        "volume": "volume_r",
        "issue": "issue_r",
        "pages": "pages_r",
        "apa_ref": "apa_ref_r",
        "bibtex_ref": "bibtex_ref_r",
        "url": "url_r",
        "outcome": "outcome",
        "abstract": "abstract_r",
        "outcome_quote": "outcome_quote",
        "outcome_quote_source": "outcome_quote_source",
    }

    for k, col in mapping.items():
        if has_col(row, col):
            out[k] = to_jsonable(row.get(col))

    if out.get("doi"):
        out["doi"] = normalize_doi(out["doi"])
    if out.get("doi_hash") is not None:
        out["doi_hash"] = str(out["doi_hash"]).strip().lower()

    for k in ("volume", "issue", "pages"):
        if k in out:
            out[k] = to_str_or_none(out[k])

    if out.get("type") is not None:
        out["type"] = norm_rep_type(out["type"])

    return out


def build_reproduction_only_entry(row: pd.Series) -> dict:
    """Reproduction row where doi_r is missing → stored in record.reproductions[]."""
    out = {}
    mapping = {
        "type": "type",
        "title": "title_r",
        "authors": "author_r",
        "journal": "journal_r",
        "year": "year_r",
        "volume": "volume_r",
        "issue": "issue_r",
        "pages": "pages_r",
        "apa_ref": "apa_ref_r",
        "bibtex_ref": "bibtex_ref_r",
        "url": "url_r",
        "outcome": "outcome",
        "abstract": "abstract_r",
        "outcome_quote": "outcome_quote",
        "outcome_quote_source": "outcome_quote_source",
    }

    for k, col in mapping.items():
        if has_col(row, col):
            out[k] = to_jsonable(row.get(col))

    for k in ("volume", "issue", "pages"):
        if k in out:
            out[k] = to_str_or_none(out[k])

    out["type"] = norm_rep_type(out.get("type"))
    return out


def build_replication_only_entry(row: pd.Series) -> dict:
    """Replication row where doi_r is missing → stored in record.replications[] (no doi)."""
    out = {}
    mapping = {
        "type": "type",
        "title": "title_r",
        "authors": "author_r",
        "journal": "journal_r",
        "year": "year_r",
        "volume": "volume_r",
        "issue": "issue_r",
        "pages": "pages_r",
        "apa_ref": "apa_ref_r",
        "bibtex_ref": "bibtex_ref_r",
        "url": "url_r",
        "outcome": "outcome",
        "abstract": "abstract_r",
        "outcome_quote": "outcome_quote",
        "outcome_quote_source": "outcome_quote_source",
    }

    for k, col in mapping.items():
        if has_col(row, col):
            out[k] = to_jsonable(row.get(col))

    for k in ("volume", "issue", "pages"):
        if k in out:
            out[k] = to_str_or_none(out[k])

    out["type"] = norm_rep_type(out.get("type"))
    return out


def merge_doi_meta_from_entry(doi_obj: dict, entry: dict):
    """Merge DOI-level metadata from an entry WITHOUT overwriting existing."""
    set_if_missing(doi_obj, "doi_hash", entry.get("doi_hash"))
    set_if_missing(doi_obj, "title", entry.get("title"))
    set_if_missing(doi_obj, "authors", entry.get("authors"))
    set_if_missing(doi_obj, "journal", entry.get("journal"))
    set_if_missing(doi_obj, "year", entry.get("year"))

    set_if_missing(doi_obj, "volume", to_str_or_none(entry.get("volume")))
    set_if_missing(doi_obj, "issue", to_str_or_none(entry.get("issue")))
    set_if_missing(doi_obj, "pages", to_str_or_none(entry.get("pages")))

    set_if_missing(doi_obj, "apa_ref", entry.get("apa_ref"))
    set_if_missing(doi_obj, "bibtex_ref", entry.get("bibtex_ref"))
    set_if_missing(doi_obj, "url", entry.get("url"))


def dedupe_append_by_doi(arr: list, item: dict):
    """Append if no existing item has same doi."""
    doi = item.get("doi")
    if not doi:
        return
    if not any(x.get("doi") == doi for x in arr):
        arr.append(item)


# -----------------------------
# DynamoDB utilities
# -----------------------------

def clear_table(table_name: str):
    """Clears a DynamoDB table by scanning and deleting keys (dev only)."""
    ddb = boto3.resource("dynamodb", region_name=AWS_REGION)
    tbl = ddb.Table(table_name)
    keys = [k["AttributeName"] for k in tbl.key_schema]
    start_key = None
    deleted = 0

    while True:
        kwargs = {}
        if start_key:
            kwargs["ExclusiveStartKey"] = start_key

        resp = tbl.scan(**kwargs)
        items = resp.get("Items", [])
        if not items:
            break

        with tbl.batch_writer() as batch:
            for it in items:
                batch.delete_item(Key={k: it[k] for k in keys})
                deleted += 1

        start_key = resp.get("LastEvaluatedKey")
        if not start_key:
            break

    print(f"Cleared {deleted} items from {table_name}")


# -----------------------------
# Main
# -----------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python etl/build_two_tables_doi_records.py <csv_file>", file=sys.stderr)
        sys.exit(2)

    csv_path = sys.argv[1]
    df = pd.read_csv(csv_path, encoding="utf-8", engine="python", on_bad_lines="warn")

    required = {"doi_o", "doi_o_hash", "type"}
    missing = [c for c in required if c not in set(map(str, df.columns))]
    if missing:
        print("ERROR missing required columns:", missing, file=sys.stderr)
        print("Found:", list(df.columns), file=sys.stderr)
        sys.exit(3)

    prefix_index: dict[str, set[str]] = defaultdict(set)
    doi_records: dict[str, dict] = {}

    # Top-level DOI role tracking
    doi_types: dict[str, set[str]] = defaultdict(set)

    # In-memory dedupe set for reproduction-only rows (per doi_o)
    reproduction_seen: dict[str, set[str]] = defaultdict(set)

    # In-memory dedupe set for replication-only rows (per doi_o)
    replication_seen: dict[str, set[str]] = defaultdict(set)

    for _, row in df.iterrows():
        doi_o = normalize_doi(row.get("doi_o"))
        doi_r = normalize_doi(row.get("doi_r")) if has_col(row, "doi_r") else ""
        rep_type = norm_rep_type(row.get("type"))

        # Prefix indexing (both sides)
        raw_o_hash = row.get("doi_o_hash")
        if pd.notna(raw_o_hash) and doi_o:
            pfx_o = str(raw_o_hash).strip().lower()[:PREFIX_LEN]
            if pfx_o:
                prefix_index[pfx_o].add(doi_o)

        if has_col(row, "doi_r_hash"):
            raw_r_hash = row.get("doi_r_hash")
            if pd.notna(raw_r_hash) and doi_r:
                pfx_r = str(raw_r_hash).strip().lower()[:PREFIX_LEN]
                if pfx_r:
                    prefix_index[pfx_r].add(doi_r)

        if not doi_o:
            if doi_r:
                rep_entry = build_replication_entry(row)
                rec_r = get_or_create(doi_records, doi_r)
                merge_doi_meta_from_entry(rec_r, rep_entry)

                if is_reproduction_type(rep_type):
                    doi_types[doi_r].add("reproduction")
                else:
                    doi_types[doi_r].add("replication")

            continue

        # Original-side DOI is always an original
        doi_types[doi_o].add("original")

        orig_entry = build_original_entry(row)

        # Case 1: two-way link exists (doi_o + doi_r)
        if doi_r:
            rep_entry = build_replication_entry(row)

            rec_o = get_or_create(doi_records, doi_o)
            merge_doi_meta_from_entry(rec_o, orig_entry)

            if is_reproduction_type(rep_type):
                doi_types[doi_r].add("reproduction")
                dedupe_append_by_doi(rec_o["record"]["reproductions"], rep_entry)
            else:
                doi_types[doi_r].add("replication")
                dedupe_append_by_doi(rec_o["record"]["replications"], rep_entry)

            rec_r = get_or_create(doi_records, doi_r)
            merge_doi_meta_from_entry(rec_r, rep_entry)
            dedupe_append_by_doi(rec_r["record"]["originals"], orig_entry)

        # Case 2: doi_r missing → either reproduction-only OR replication-only
        else:
            rec_o = get_or_create(doi_records, doi_o)
            merge_doi_meta_from_entry(rec_o, orig_entry)

            if is_reproduction_type(rep_type):
                repro_entry = build_reproduction_only_entry(row)

                fp = stable_id_from_fields(
                    str(repro_entry.get("title") or ""),
                    str(repro_entry.get("year") or ""),
                    str(repro_entry.get("journal") or ""),
                    str(repro_entry.get("apa_ref") or ""),
                    str(repro_entry.get("url") or ""),
                    str(repro_entry.get("bibtex_ref") or ""),
                    str(repro_entry.get("outcome") or ""),
                    str(repro_entry.get("outcome_quote") or ""),
                )

                if fp not in reproduction_seen[doi_o]:
                    rec_o["record"]["reproductions"].append(repro_entry)
                    reproduction_seen[doi_o].add(fp)

            else:
                rep_only_entry = build_replication_only_entry(row)

                fp = stable_id_from_fields(
                    str(rep_only_entry.get("type") or ""),
                    str(rep_only_entry.get("title") or ""),
                    str(rep_only_entry.get("year") or ""),
                    str(rep_only_entry.get("journal") or ""),
                    str(rep_only_entry.get("apa_ref") or ""),
                    str(rep_only_entry.get("url") or ""),
                    str(rep_only_entry.get("bibtex_ref") or ""),
                    str(rep_only_entry.get("outcome") or ""),
                    str(rep_only_entry.get("outcome_quote") or ""),
                )

                if fp not in replication_seen[doi_o]:
                    rec_o["record"]["replications"].append(rep_only_entry)
                    replication_seen[doi_o].add(fp)

    # Compute coherent stats
    for _, record in doi_records.items():
        reps = record["record"]["replications"]
        repros = record["record"]["reproductions"]
        origs = record["record"]["originals"]

        uniq_ori = {x.get("doi") for x in origs if x.get("doi")}

        rep_with_doi = sum(1 for x in reps if x.get("doi"))
        rep_only = sum(1 for x in reps if not x.get("doi"))
        uniq_rep_dois = {x.get("doi") for x in reps if x.get("doi")}

        repro_with_doi = sum(1 for x in repros if x.get("doi"))
        repro_only = sum(1 for x in repros if not x.get("doi"))

        record["record"]["stats"] = {
            "n_replications_total": len(reps),
            "n_replications_with_doi": rep_with_doi,
            "n_replications_only": rep_only,
            "n_unique_replication_dois": len(uniq_rep_dois),

            "n_reproductions_total": len(repros),
            "n_reproductions_with_doi": repro_with_doi,
            "n_reproductions_only": repro_only,

            "n_originals_total": len(origs),
            "n_unique_original_dois": len(uniq_ori),
        }

        # Citation graph fields (computed from replications)
        outcome_mix: dict[str, int] = {}
        citation_timeline: dict[str, int] = {}
        first_year: int | None = None
        first_outcome: str | None = None
        for rep in reps:
            outcome = rep.get("outcome")
            if outcome:
                outcome_mix[outcome] = outcome_mix.get(outcome, 0) + 1
            rep_year = rep.get("year")
            if rep_year:
                try:
                    y = int(rep_year)
                    citation_timeline[str(y)] = citation_timeline.get(str(y), 0) + 1
                    if first_year is None or y < first_year:
                        first_year = y
                        first_outcome = outcome
                except (ValueError, TypeError):
                    pass
        record["record"]["outcome_mix"] = outcome_mix
        record["record"]["citation_timeline"] = citation_timeline
        record["record"]["first_replication_year"] = str(first_year) if first_year is not None else None
        record["record"]["first_replication_outcome"] = first_outcome

    # Finalize top-level DOI roles in stable order
    type_order = ["original", "replication", "reproduction"]
    for doi, record in doi_records.items():
        roles = doi_types.get(doi, set())
        record["types"] = [t for t in type_order if t in roles]

    print(f"Prepared {len(prefix_index)} prefixes and {len(doi_records)} doi records")

    ddb = boto3.resource("dynamodb", region_name=AWS_REGION)
    prefix_tbl = ddb.Table(PREFIX_TABLE)
    doi_tbl = ddb.Table(DOI_TABLE)
    search_tbl = ddb.Table(SEARCH_TABLE)

    if CLEAR_TABLES:
        clear_table(PREFIX_TABLE)
        clear_table(DOI_TABLE)
        clear_table(SEARCH_TABLE)
    else:
        print("CLEAR_TABLES=0 → not clearing tables")

    # Write PREFIX table
    with prefix_tbl.batch_writer(overwrite_by_pkeys=["prefix"]) as batch:
        for prefix, dois in prefix_index.items():
            batch.put_item(
                Item={
                    "prefix": prefix,
                    "dois": sorted(list(dois)),
                }
            )

    # Write DOI table
    with doi_tbl.batch_writer(overwrite_by_pkeys=["doi"]) as batch:
        for doi, record in doi_records.items():
            batch.put_item(
                Item={
                    "doi": doi,
                    "record": json.dumps(record, ensure_ascii=False),
                }
            )

    def extract_author_names(raw_authors) -> list[str]:
        """Normalize an authors field (list of dicts, list of strings, or CSV string) to names."""
        if not raw_authors:
            return []
        if isinstance(raw_authors, list):
            names = []
            for a in raw_authors:
                if isinstance(a, dict):
                    given = str(a.get("given") or "").strip()
                    family = str(a.get("family") or "").strip()
                    name = f"{given} {family}".strip()
                else:
                    name = str(a).strip()
                if name:
                    names.append(name)
            return names
        return [n.strip() for n in str(raw_authors).split(",") if n.strip()]

    # Build + write SEARCH INDEX table
    search_entries = []
    for doi, record in doi_records.items():
        authors = extract_author_names(record.get("authors"))

        nested = record.get("record", {})
        seen_rep: set[str] = set(authors)
        rep_authors: list[str] = []
        for entry in nested.get("replications", []) + nested.get("reproductions", []) + nested.get("originals", []):
            for name in extract_author_names(entry.get("authors")):
                if name not in seen_rep:
                    seen_rep.add(name)
                    rep_authors.append(name)

        search_entries.append(
            {
                "_doi": doi,
                "title": str(record.get("title") or ""),
                "authors": authors,
                "rep_authors": rep_authors,
                "year": str(record.get("year") or ""),
            }
        )

    chunks = [
        search_entries[i:i + SEARCH_CHUNK]
        for i in range(0, len(search_entries), SEARCH_CHUNK)
    ]
    total_chunks = len(chunks)

    with search_tbl.batch_writer(overwrite_by_pkeys=["chunk_id"]) as batch:
        batch.put_item(
            Item={
                "chunk_id": "meta",
                "data": str(total_chunks),
            }
        )

        for idx, chunk in enumerate(chunks):
            batch.put_item(
                Item={
                    "chunk_id": str(idx),
                    "data": json.dumps(chunk, ensure_ascii=False),
                }
            )

    print(f"Wrote {total_chunks} search index chunks ({len(search_entries)} entries)")
    print("Done.")


if __name__ == "__main__":
    main()
