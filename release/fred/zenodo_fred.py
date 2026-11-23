"""Assemble and deposit FReD versions on Zenodo.

Assembly is offline. Upload needs ZENODO_TOKEN (or ZENODO_SANDBOX_TOKEN with
--sandbox) and, for production, --approve-production after the bundle was approved.

  python3 release/fred/zenodo_fred.py assemble 2025.11.1 BUNDLE_DIR
  python3 release/fred/zenodo_fred.py upload BUNDLE_DIR [--previous PREV_BUNDLE_DIR] \
      --approve-production [--publish]

Upload saves zenodo-state.json in the bundle immediately after creating the draft;
re-running the same command resumes that draft instead of creating another.
"""
import argparse
import csv
import datetime as dt
import hashlib
import html
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import openpyxl
import requests
import yaml

ROOT = Path(__file__).resolve().parents[2]
CONF = Path(__file__).resolve().parent
API = {"production": "https://zenodo.org/api", "sandbox": "https://sandbox.zenodo.org/api"}
LOCAL_ONLY = {"zenodo-metadata.json", "zenodo-state.json"}  # kept in the bundle, not deposited


def load_conf():
    return yaml.safe_load((CONF / "versions.yml").read_text(encoding="utf-8"))


def creators(kind):
    c = yaml.safe_load((CONF / "creators.yml").read_text(encoding="utf-8"))
    people = [dict(p) for p in c["smart"]]
    for add in (c.get("additions") or {}).get(kind, []) if kind != "smart" else []:
        add = dict(add)
        after = add.pop("after")
        idx = [p["name"] for p in people].index(after)
        people.insert(idx + 1, add)
    names = [p["name"] for p in people]
    assert len(names) == len(set(names)), "duplicate creator"
    return people


def cell_text(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    if isinstance(v, (dt.datetime, dt.date)):
        return v.isoformat()
    return str(v)


def read_values(path):
    """Header and typed cell values of the first worksheet."""
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True).worksheets[0]
    ws.reset_dimensions()  # some writers store a stale dimension, which truncates reads
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    while rows and all(v is None or v == "" for v in rows[-1]):
        rows.pop()
    header = rows[0]
    assert all(header) and len(header) == len(set(header)), f"bad header in {path}"
    return list(header), [r[: len(header)] + [None] * (len(header) - len(r)) for r in rows[1:]]


def read_sheet(path):
    header, rows = read_values(path)
    return header, [[cell_text(v) for v in r] for r in rows]


def write_csv(path, header, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\r\n")
        w.writerow(header)
        w.writerows(rows)


def write_xlsx(path, header, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(header)
    for r in rows:
        ws.append(r)
    wb.save(path)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def md5(path):
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


def git_commit():
    return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()


def cff(conf, version, people, doi=None):
    authors = []
    for p in people:
        family, given = [x.strip() for x in p["name"].split(",", 1)]
        a = {"family-names": family, "given-names": given}
        if p.get("orcid"):
            a["orcid"] = f"https://orcid.org/{p['orcid']}"
        authors.append(a)
    data = {
        "cff-version": "1.2.0",
        "message": "If you use this dataset, please cite this version using the metadata from this file.",
        "type": "dataset",
        "title": conf["title"],
        "version": version,
        "authors": authors,
        "license": "CC-BY-4.0",
        "repository-code": "https://github.com/forrtproject/fred-data",
        "keywords": conf["keywords"],
    }
    if doi:
        data["doi"] = doi
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100)


def assemble(version, bundle):
    conf = load_conf()
    v = conf["versions"][version]
    bundle = Path(bundle)
    if bundle.exists():
        sys.exit(f"Refusing to overwrite existing bundle {bundle}")
    bundle.mkdir(parents=True)
    people = creators(v["creators"])

    header, rows = read_sheet(ROOT / v["data"])
    write_csv(bundle / "fred.csv", header, rows)
    shutil.copyfile(ROOT / v["data"], bundle / "fred.xlsx")

    cb_header, cb_rows = read_sheet(ROOT / v["codebook"])
    for add in v.get("codebook_additions", []):
        cb_rows.append([add.get(h, "") for h in cb_header])
    documented = {r[cb_header.index("Variable")] for r in cb_rows}
    missing = [h for h in header if h not in documented]
    assert not missing, f"columns missing from codebook: {missing}"
    write_csv(bundle / "fred_codebook.csv", cb_header, cb_rows)
    write_xlsx(bundle / "fred_codebook.xlsx", cb_header, cb_rows)

    for name, src in (v.get("extra_files") or {}).items():
        shutil.copyfile(ROOT / src, bundle / name)

    # Row counts for README and description
    col = header.index(v["score_column"])
    prefix = v.get("score_prefix")
    is_score = [(r[col].startswith(prefix) if prefix else r[col] == "TRUE") for r in rows]
    counts = {"effects": len(rows), "score_effects": sum(is_score), "columns": len(header)}
    counts["forrt_effects"] = counts["effects"] - counts["score_effects"]

    (bundle / "CITATION.cff").write_text(cff(conf, version, people), encoding="utf-8")
    (bundle / "CHANGELOG.md").write_text(
        f"# FReD {version}\n\n" + "\n".join(f"- {c}" for c in v["changes"]) + "\n", encoding="utf-8")
    (bundle / "README.md").write_text(readme(conf, version, v, counts), encoding="utf-8")
    provenance = {
        "version": version,
        "assembled_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "fred_data_commit": git_commit(),
        "data_source": v["data"],
        "data_source_sha256": sha256(ROOT / v["data"]),
        "build_command": v.get("build"),
        "counts": counts,
    }
    (bundle / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    meta = metadata(conf, version, v, people, counts)
    (bundle / "zenodo-metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
                                                 encoding="utf-8")
    write_checksums(bundle)
    print(json.dumps(counts))


def readme(conf, version, v, counts):
    lines = [
        f"# {conf['title']}, version {version}", "",
        "FReD is an effect-level database of replication attempts in the social and behavioural",
        "sciences. Each row pairs one original effect with one replication effect: sample sizes,",
        "effect sizes, p-values, and the outcome as reported by the replication authors.", "",
        " ".join(v["summary"].split()), "",
        f"This version has {counts['effects']:,} effects: {counts['forrt_effects']:,} coded by FORRT "
        f"and {counts['score_effects']:,} from COS's SCORE programme.", "",
        "## Files", "",
        "- `fred.csv`: the data, UTF-8 with BOM; empty cells are missing values. Some text cells begin",
        "  with `=` or `@` (calculation notes in `es_repr_*`, BibTeX entries), which spreadsheet programs",
        "  may try to evaluate. Read the CSV with a CSV parser (e.g., R or Python), or use `fred.xlsx`.",
        "- `fred.xlsx`: the same data as an Excel workbook.",
        "- `fred_codebook.csv` and `fred_codebook.xlsx`: variable definitions.",
    ]
    for name in (v.get("extra_files") or {}):
        lines.append(f"- `{name}`: see notes below.")
    lines += [
        "- `CHANGELOG.md`: what changed in this version.",
        "- `CITATION.cff`: how to cite this version, with its DOI.",
        "- `provenance.json`: source file, its SHA-256 hash and the fred-data commit used.",
        "- `checksums.json`: SHA-256 hashes of the deposited files.", "",
        "## Notes", "",
    ]
    lines += [f"- {n}" for n in v.get("notes", [])]
    ack = " ".join(conf["cos_acknowledgement"].split()).format(marker=v["score_marker"])
    lines += [
        "", "## SCORE data and the Center for Open Science", "",
        ack, "",
    ]
    lines += [f"- {r}" for r in conf["cos_references"]]
    lines += [
        "", "## Licence and maintenance", "",
        "CC BY 4.0. Maintained by FORRT (https://forrt.org/replication-hub/) in",
        "https://github.com/forrtproject/fred-data. Report errors as issues there.",
        "The companion article-level database, FLoRA, is at https://doi.org/10.5281/zenodo.24461022.", "",
    ]
    return "\n".join(lines)


def metadata(conf, version, v, people, counts):
    e = html.escape
    desc = [
        "<p>FReD is an effect-level database of replication attempts in the social and behavioural "
        "sciences. Each row pairs one original effect with one replication effect: sample sizes, effect "
        "sizes, p-values, and the outcome as reported by the replication authors.</p>",
        f"<p>{e(' '.join(v['summary'].split()))}</p>",
        f"<p>This version has {counts['effects']:,} effects: {counts['forrt_effects']:,} coded by FORRT and "
        f"{counts['score_effects']:,} from COS's SCORE programme.</p>",
        "<p><strong>Changes in this version</strong></p><ul>"
        + "".join(f"<li>{e(c)}</li>" for c in v["changes"]) + "</ul>",
        f"<p><strong>SCORE data and the Center for Open Science.</strong> {e(' '.join(conf['cos_acknowledgement'].split()).format(marker=v['score_marker']))}</p><ul>"
        + "".join(f"<li>{e(r)}</li>" for r in conf["cos_references"]) + "</ul>",
        "<p>The companion article-level database, FLoRA, is at "
        "<a href=\"https://doi.org/10.5281/zenodo.24461022\">https://doi.org/10.5281/zenodo.24461022</a>. "
        "More information: <a href=\"https://forrt.org/replication-hub/\">https://forrt.org/replication-hub/</a>.</p>",
    ]
    return {
        "title": conf["title"],
        "upload_type": "dataset",
        "publication_date": dt.date.today().isoformat(),
        "version": version,
        "creators": people,
        "description": "".join(desc),
        "license": conf["license"],
        "access_right": "open",
        "keywords": conf["keywords"],
        "related_identifiers": conf["related_identifiers"],
    }


def deposit_files(bundle):
    return sorted(p.name for p in Path(bundle).iterdir() if p.is_file() and p.name not in LOCAL_ONLY)


def checksummed_files(bundle):
    return [f for f in deposit_files(bundle) if f != "checksums.json"]


def write_checksums(bundle):
    sums = {name: sha256(Path(bundle) / name) for name in checksummed_files(bundle)}
    (Path(bundle) / "checksums.json").write_text(json.dumps(sums, indent=2) + "\n", encoding="utf-8")


def verify_checksums(bundle, allow_cff_change=False):
    sums = json.loads((Path(bundle) / "checksums.json").read_text())
    files = checksummed_files(bundle)
    assert set(files) == set(sums), f"bundle files differ from checksums.json: {sorted(set(files) ^ set(sums))}"
    for name, h in sums.items():
        if name == "CITATION.cff" and allow_cff_change:
            continue
        assert sha256(Path(bundle) / name) == h, f"{name} changed since assembly"


class Zenodo:
    def __init__(self, env):
        var = "ZENODO_TOKEN" if env == "production" else "ZENODO_SANDBOX_TOKEN"
        token = os.environ.get(var)
        if not token:
            sys.exit(f"{var} is not set")
        self.api = API[env]
        self.s = requests.Session()
        self.s.headers["Authorization"] = f"Bearer {token}"

    def call(self, method, url, **kw):
        r = self.s.request(method, url if url.startswith("http") else self.api + url, timeout=600, **kw)
        if r.status_code >= 400:
            sys.exit(f"Zenodo {method} {url.split('?')[0]} failed with HTTP {r.status_code}")
        return r.json() if r.content else {}


def upload(bundle, previous, env, approve, publish, resume):
    bundle = Path(bundle)
    if env == "production" and not approve:
        sys.exit("Production upload needs --approve-production (after the bundle was approved)")
    state_path = bundle / "zenodo-state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    if state.get("published"):
        sys.exit(f"Already published: {state['doi']}")
    verify_checksums(bundle, allow_cff_change=bool(state))
    meta = json.loads((bundle / "zenodo-metadata.json").read_text(encoding="utf-8"))
    z = Zenodo(env)

    if state:
        assert state["environment"] == env and state["version"] == meta["version"], "state mismatch"
        dep = z.call("GET", f"/deposit/depositions/{state['id']}")
    elif resume:
        dep = z.call("GET", f"/deposit/depositions/{resume}")
        assert not dep["submitted"], "resume target is already published"
    else:
        if previous:
            prev = json.loads((Path(previous) / "zenodo-state.json").read_text())
            assert prev["environment"] == env and prev.get("published"), "previous bundle not published here"
            nv = z.call("POST", f"/deposit/depositions/{prev['id']}/actions/newversion")
            dep = z.call("GET", nv["links"]["latest_draft"])
            for f in dep.get("files", []):
                z.call("DELETE", f"/deposit/depositions/{dep['id']}/files/{f['id']}")
        else:
            dep = z.call("POST", "/deposit/depositions", json={})
    doi = dep["metadata"].get("prereserve_doi", {}).get("doi")
    assert doi, "Zenodo returned no reserved DOI"
    state = {"environment": env, "id": dep["id"], "conceptrecid": dep.get("conceptrecid"),
             "version": meta["version"], "doi": doi, "published": False}
    state_path.write_text(json.dumps(state, indent=2) + "\n")

    # Write the reserved DOI into CITATION.cff, then refresh its checksum.
    conf = load_conf()
    v = conf["versions"][meta["version"]]
    (bundle / "CITATION.cff").write_text(cff(conf, meta["version"], creators(v["creators"]), doi), encoding="utf-8")
    sums = json.loads((bundle / "checksums.json").read_text())
    sums["CITATION.cff"] = sha256(bundle / "CITATION.cff")
    (bundle / "checksums.json").write_text(json.dumps(sums, indent=2) + "\n", encoding="utf-8")

    files = deposit_files(bundle)
    remote = {f["filename"]: f for f in z.call("GET", f"/deposit/depositions/{dep['id']}/files")}
    for name in files:
        if name in remote and remote[name]["checksum"] == md5(bundle / name):
            continue
        if name in remote:
            z.call("DELETE", f"/deposit/depositions/{dep['id']}/files/{remote[name]['id']}")
        with open(bundle / name, "rb") as fh:
            z.call("PUT", f"{dep['links']['bucket']}/{name}", data=fh)
    remote = {f["filename"]: f["checksum"] for f in z.call("GET", f"/deposit/depositions/{dep['id']}/files")}
    expected = {name: md5(bundle / name) for name in files}
    assert remote == expected, f"remote files differ: {sorted(set(remote.items()) ^ set(expected.items()))}"

    meta = dict(meta, prereserve_doi=True)
    z.call("PUT", f"/deposit/depositions/{dep['id']}", json={"metadata": meta})
    if publish:
        pub = z.call("POST", f"/deposit/depositions/{dep['id']}/actions/publish")
        state.update(published=True, doi=pub["doi"], conceptrecid=pub["conceptrecid"],
                     url=pub["links"]["html"])
    state_path.write_text(json.dumps(state, indent=2) + "\n")
    print(json.dumps(state))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("assemble")
    a.add_argument("version")
    a.add_argument("bundle")
    u = sub.add_parser("upload")
    u.add_argument("bundle")
    u.add_argument("--previous")
    u.add_argument("--sandbox", action="store_true")
    u.add_argument("--approve-production", action="store_true")
    u.add_argument("--publish", action="store_true")
    u.add_argument("--resume-deposit", type=int)
    args = ap.parse_args()
    if args.cmd == "assemble":
        assemble(args.version, args.bundle)
    else:
        upload(args.bundle, args.previous, "sandbox" if args.sandbox else "production",
               args.approve_production, args.publish, args.resume_deposit)


if __name__ == "__main__":
    main()
