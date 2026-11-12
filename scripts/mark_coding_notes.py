"""Mark coder-written notes in flora.csv's quote sources (FReD-data#173).

Some rows hold a coder's note in the outcome quote rather than a quotation from the
report. This step prefixes the matching source with "coding note: " so downstream
tools such as FLoRA Explorer can tell notes from quotations. A source part is marked
when
  - it consists of exactly one known basis of a note (the RP:P data file, a comment
    on FReD-data#19, a project rule), or
  - it belongs to 10.1098/rsos.231240 and its quote part is the rewritten
    "Subjective replication success rating = ..." note.

Sources are split on "||" and each part is matched with the quote part in the same
position, so the prefix stays aligned. Replications are marked in
outcome_quote_source. Reproductions are marked in their own per-axis columns
(out_quote_computational_source, out_quote_robust_source); their combined
outcome_quote_source is left as flora-validation builds it. The step is idempotent:
a part that already carries the prefix is not marked again.

The values come from the FLoRA entry sheets via forrtproject/flora-validation; this
step stands in until they are marked there.

Usage: python3 scripts/mark_coding_notes.py output/flora.csv
"""
import csv
import io
import re
import sys

PREFIX = "coding note: "

# Bases of coder-written notes, matched against a whole source part.
NOTE_BASIS = re.compile(
    r"data file at https://osf\.io/fgjvw"
    r"|https://github\.com/forrtproject/FReD-data/issues/19#issuecomment-\d+"
    r"|project rule",
    re.IGNORECASE,
)
# Soto et al.'s ratings, rewritten into a note by flora-validation's cos_quote_rewrite.
RATING_DOI = "10.1098/rsos.231240"
RATING_NOTE = re.compile(r"Subjective replication success rating =")
SEPARATOR = re.compile(r"(\s*\|\|\s*)")

# Source column -> quote column it describes, per row type.
COLUMNS = {
    "replication": {"outcome_quote_source": "outcome_quote"},
    "reproduction": {"out_quote_computational_source": "outcome_computational_quote",
                     "out_quote_robust_source": "outcome_robustness_quote"},
}


def mark_source(source, quote="", doi=""):
    # Odd indices are the separators, kept verbatim so unchanged parts stay identical.
    pieces = SEPARATOR.split(source)
    parts = pieces[::2]
    quotes = SEPARATOR.split(quote)[::2]
    aligned = len(quotes) == len(parts)
    for i, part in enumerate(parts):
        body = part.strip()
        if not body or body.lower().startswith(PREFIX.strip()):
            continue
        rating = (doi.lower() == RATING_DOI and aligned
                  and RATING_NOTE.match(quotes[i].strip()))
        if NOTE_BASIS.fullmatch(body) or rating:
            pieces[2 * i] = part.replace(body, PREFIX + body, 1)
    return "".join(pieces)


def main(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    at = {name: header.index(name) for name in header}
    changed = 0
    for row in rows[1:]:
        before = list(row)
        for source, quote in COLUMNS.get(row[at["type"]], {}).items():
            row[at[source]] = mark_source(row[at[source]], row[at[quote]],
                                          row[at["doi_r"]])
        changed += row != before
    # flora.csv is written with every field quoted and \n line ends; this writer
    # reproduces it byte for byte, so only the marked cells change.
    out = io.StringIO(newline="")
    csv.writer(out, quoting=csv.QUOTE_ALL, lineterminator="\n").writerows(rows)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        f.write(out.getvalue())
    print(f"Marked coding-note sources in {changed} rows")


if __name__ == "__main__":
    main(sys.argv[1])
