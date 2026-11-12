"""Mark coder-written notes in flora.csv's outcome_quote_source (FReD-data#173).

Some rows hold a coder's note in outcome_quote rather than a quotation from the
report. Their source names the basis of the note (a data file, a GitHub comment, a
project rule), which the entry sheets record without marking it as a note. This step
prefixes those source parts with "coding note: " so downstream tools such as FLoRA
Explorer can tell notes from quotations.

The prefix is applied per "||" part, so it stays aligned with the parts of
outcome_quote, and after a "Computational:"/"Robustness:" label if one is present.
Only parts that consist of exactly one of the known bases are changed. The step is
idempotent: a part that already carries the prefix no longer matches.

The values come from the FLoRA entry sheets via forrtproject/flora-validation; this
step stands in until they are marked there.

Usage: python3 scripts/mark_coding_notes.py output/flora.csv
"""
import csv
import io
import re
import sys

PREFIX = "coding note: "
COLUMN = "outcome_quote_source"

# Bases of coder-written notes, matched against a whole source part.
NOTE_BASIS = re.compile(
    r"data file at https://osf\.io/fgjvw"
    r"|https://github\.com/forrtproject/FReD-data/issues/19#issuecomment-\d+"
    r"|project rule",
    re.IGNORECASE,
)
LABEL = re.compile(r"((?:Computational|Robustness):\s*)?(.*)", re.DOTALL)
SEPARATOR = re.compile(r"(\s*\|\|\s*)")


def mark_part(part):
    label, body = LABEL.fullmatch(part).groups()
    if NOTE_BASIS.fullmatch(body.strip()):
        return (label or "") + PREFIX + body
    return part


def mark_source(value):
    # Odd indices are the separators, kept verbatim so unchanged parts stay identical.
    pieces = SEPARATOR.split(value)
    return "".join(p if i % 2 else mark_part(p) for i, p in enumerate(pieces))


def main(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    col = rows[0].index(COLUMN)
    changed = 0
    for row in rows[1:]:
        new = mark_source(row[col])
        if new != row[col]:
            row[col] = new
            changed += 1
    # flora.csv is written with every field quoted and \n line ends; this writer
    # reproduces it byte for byte, so only the marked cells change.
    out = io.StringIO(newline="")
    csv.writer(out, quoting=csv.QUOTE_ALL, lineterminator="\n").writerows(rows)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        f.write(out.getvalue())
    print(f"Marked {changed} rows' {COLUMN} as coding notes")


if __name__ == "__main__":
    main(sys.argv[1])
