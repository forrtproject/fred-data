# 🔍 FORRT Replication Database — Lightweight API (DOI-Centric)

This backend powers the **FORRT Replication Database (lightweight version)** and the **Zotero Replication Checker** plugin.

It exposes a small API that lets clients query replication/reproduction links using either:

1. **Privacy-preserving 3-character DOI hash prefixes**
2. **Full DOIs** (direct lookup)

---

## Base URLs

We run two separate deployments:

**Primary API (Dev1)**

```txt
https://rep-api.forrt.org/v1
```

**Test API (Dev0)**

```txt
https://80zw14hxjc.execute-api.eu-central-1.amazonaws.com/v1
```

---

## Table of Contents

* [Overview](#overview)
* [How Data Is Stored](#how-data-is-stored)
* [Quick Start](#quick-start)
* [Endpoints](#endpoints)

  * [1) Prefix Lookup (privacy-preserving)](#1-prefix-lookup-privacy-preserving)
  * [2) DOI Lookup (direct)](#2-doi-lookup-direct)
* [Response Model](#response-model)
* [Headers](#headers)
* [Error Responses](#error-responses)
* [Testing Snippets](#testing-snippets)
* [Functions & Source](#functions--source)
* [Notes](#notes)

---

## Overview

### Two lookup modes

1. **Prefix Lookup**
   Query by **3-character prefixes** derived from DOI hashes.

2. **DOI Lookup**
   Query by full DOIs. The endpoint name is  `/original-lookup` but it returns the record for **any DOI** (original, replication, and reproduction).

### CORS + caching

All endpoints are **CORS enabled** and return cacheable responses.

---

## How Data Is Stored

This system uses **two DynamoDB tables**:

### 1) PREFIX_TABLE

**Key:** `prefix` (string, 3 chars)
**Value:** `dois` (List of strings)

A prefix can map to DOIs coming from:

* `doi_o_hash[:3] → doi_o`
* `doi_r_hash[:3] → doi_r`

This means **the same prefix endpoint supports searching “original-side” and “replication and reproduction -side” hashes** without changing the API.

### 2) DOI_TABLE

**Key:** `doi` (string)
**Value:** `record` (JSON string)

Each DOI has exactly **one JSON record**, containing:

* the DOI’s metadata (title, journal, year, etc.)
* relationship lists:

  * `record.replications[]` (this DOI is the original; links to replications)
  * `record.originals[]` (this DOI is a replication; links to originals)
  * `record.reproductions[]` (reproduction rows that have **no doi_r**, stored under doi_o)

The ETL builds all links once, so the API reads fast.

---

## Quick Start

### Prefix lookup (GET)

**Primary**

```bash
curl "https://rep-api.forrt.org/v1/prefix-lookup?prefixes=198"
```

**Test**

```bash
curl "https://80zw14hxjc.execute-api.eu-central-1.amazonaws.com/v1/prefix-lookup?prefixes=198"
```

---

### DOI lookup (GET)

> ✅ Important: the query param is **`dois`** (plural), not `doi`.

**Primary**

```bash
curl "https://rep-api.forrt.org/v1/original-lookup?dois=10.1037/a0027598"
```

**Test**

```bash
curl "https://80zw14hxjc.execute-api.eu-central-1.amazonaws.com/v1/original-lookup?dois=10.1037/a0027598"
```

---

## Endpoints

## 1) Prefix Lookup (privacy-preserving)

Looks up DOI records using **3-character hash prefixes** (privacy-first).

✅ Supports prefixes for both `doi_o_hash` and `doi_r_hash`.

### Primary API

| Method | URL                                                           |
| ------ | ------------------------------------------------------------- |
| `GET`  | `https://rep-api.forrt.org/v1/prefix-lookup?prefixes=198` |
| `POST` | `https://rep-api.forrt.org/v1/prefix-lookup`                  |

### Test API

| Method | URL                                                                                           |
| ------ | --------------------------------------------------------------------------------------------- |
| `GET`  | `https://80zw14hxjc.execute-api.eu-central-1.amazonaws.com/v1/prefix-lookup?prefixes=198` |
| `POST` | `https://80zw14hxjc.execute-api.eu-central-1.amazonaws.com/v1/prefix-lookup`                  |

### Request format

**POST**

```bash
curl -X POST "https://rep-api.forrt.org/v1/prefix-lookup" \
  -H "Content-Type: application/json" \
  -d '{"prefixes":["198"]}'
```

**GET**

```bash
curl "https://rep-api.forrt.org/v1/prefix-lookup?prefixes=198"
```

### Response (200)

```json
{
"results": {
"198": [
{
"doi": "10.1016/j.jcps.2010.06.007",
"doi_hash": "198",
"title": "Effects of product unit image on consumption of snack foods",
"authors": [
{
"given": "Adriana V.",
"family": "Madzharov",
"sequence": "first"
},
{
"given": "Lauren G.",
"family": "Block",
"sequence": "additional"
}
],
"journal": "Journal of Consumer Psychology",
"year": 2010,
"volume": "20",
"issue": "4",
"pages": "398-409",
"apa_ref": "Madzharov, A. V., & Block, L. G. (2010). Effects of product unit image on consumption of snack foods. Journal of Consumer Psychology, 20(4), 398–409. Portico. https://doi.org/10.1016/j.jcps.2010.06.007",
"bibtex_ref": "@article{Madzharov_2010, title={Effects of product unit image on consumption of snack foods}, volume={20}, ISSN={1532-7663}, url={http://dx.doi.org/10.1016/j.jcps.2010.06.007}, DOI={10.1016/j.jcps.2010.06.007}, number={4}, journal={Journal of Consumer Psychology}, publisher={Wiley}, author={Madzharov, Adriana V. and Block, Lauren G.}, year={2010}, month=jul, pages={398–409} }",
"url": null,
"record": {
"stats": {
"n_replications": 1,
"n_unique_replication_dois": 1,
"n_originals": 0,
"n_unique_original_dois": 0,
"n_reproductions": 0,
"n_reproduction_only": 0
},
"replications": [
{
"doi": "10.3389/fcomm.2022.1048896",
"doi_hash": "a2c",
"rep_type": "replication",
"title": "Evaluating replicability of ten influential research on sensory marketing",
"authors": [
{
"given": "Kosuke",
"family": "Motoki",
"sequence": "first"
},
{
"given": "Sayo",
"family": "Iseki",
"sequence": "additional"
}
],
"journal": "Frontiers in Communication",
"year": 2022,
"volume": "7.0",
"issue": null,
"pages": null,
"apa_ref": "Motoki, K., & Iseki, S. (2022). Evaluating replicability of ten influential research on sensory marketing. Frontiers in Communication, 7. https://doi.org/10.3389/fcomm.2022.1048896",
"bibtex_ref": "@article{Motoki_2022, title={Evaluating replicability of ten influential research on sensory marketing}, volume={7}, ISSN={2297-900X}, url={http://dx.doi.org/10.3389/fcomm.2022.1048896}, DOI={10.3389/fcomm.2022.1048896}, journal={Frontiers in Communication}, publisher={Frontiers Media SA}, author={Motoki, Kosuke and Iseki, Sayo}, year={2022}, month=oct }",
"url": null,
"outcome": "failed",
"abstract": null,
"outcome_quote": null
}
],
"originals": [],
"reproductions": []
}
}
]
}
}
```

---

## 2) DOI Lookup (direct)

Direct lookup by DOI.

> Endpoint is still called **`/original-lookup`** for backward compatibility, but it returns the DOI record for **any DOI**.

### Primary API

| Method | URL                                                                  |
| ------ | -------------------------------------------------------------------- |
| `GET`  | `https://rep-api.forrt.org/v1/original-lookup?dois=10.1037/a0027598` |
| `POST` | `https://rep-api.forrt.org/v1/original-lookup`                       |

### Test API

| Method | URL                                                                                                  |
| ------ | ---------------------------------------------------------------------------------------------------- |
| `GET`  | `https://80zw14hxjc.execute-api.eu-central-1.amazonaws.com/v1/original-lookup?dois=10.1037/a0027598` |
| `POST` | `https://80zw14hxjc.execute-api.eu-central-1.amazonaws.com/v1/original-lookup`                       |

### Request format

**POST**

```bash
curl -X POST "https://rep-api.forrt.org/v1/original-lookup" \
  -H "Content-Type: application/json" \
  -d '{"dois":["10.1037/a0027598"]}'
```

**GET**

```bash
curl "https://rep-api.forrt.org/v1/original-lookup?dois=10.1037/a0027598"
```

### Response (200)

```json
{
"results": {
"10.1037/a0027598": {
"doi": "10.1037/a0027598",
"doi_hash": "93c",
"title": "The physical burdens of secrecy.",
"authors": [
{
"given": "Michael L.",
"family": "Slepian",
"sequence": "first"
},
{
"given": "E. J.",
"family": "Masicampo",
"sequence": "additional"
},
{
"given": "Negin R.",
"family": "Toosi",
"sequence": "additional"
},
{
"given": "Nalini",
"family": "Ambady",
"sequence": "additional"
}
],
"journal": "Journal of Experimental Psychology: General",
"year": 2012,
"volume": "141",
"issue": "4",
"pages": "619-624",
"apa_ref": "Slepian, M. L., Masicampo, E. J., Toosi, N. R., & Ambady, N. (2012). The physical burdens of secrecy. Journal of Experimental Psychology: General, 141(4), 619–624. https://doi.org/10.1037/a0027598",
"bibtex_ref": "@article{Slepian_2012, title={The physical burdens of secrecy.}, volume={141}, ISSN={0096-3445}, url={http://dx.doi.org/10.1037/a0027598}, DOI={10.1037/a0027598}, number={4}, journal={Journal of Experimental Psychology: General}, publisher={American Psychological Association (APA)}, author={Slepian, Michael L. and Masicampo, E. J. and Toosi, Negin R. and Ambady, Nalini}, year={2012}, pages={619–624} }",
"url": null,
"record": {
"stats": {
"n_replications": 2,
"n_unique_replication_dois": 2,
"n_originals": 0,
"n_unique_original_dois": 0,
"n_reproductions": 0,
"n_reproduction_only": 0
},
"replications": [
{
"doi": "10.1037/xge0000090",
"doi_hash": "f14",
"rep_type": "replication",
"title": "The burden of secrecy? No effect on hill slant estimation and beanbag throwing.",
"authors": [
{
"given": "Diane",
"family": "Pecher",
"sequence": "first"
},
{
"given": "Heleen",
"family": "van Mierlo",
"sequence": "additional"
},
{
"given": "Rouwen",
"family": "Cañal-Bruland",
"sequence": "additional"
},
{
"given": "René",
"family": "Zeelenberg",
"sequence": "additional"
}
],
"journal": "Journal of Experimental Psychology: General",
"year": 2015,
"volume": "144.0",
"issue": "4",
"pages": "e65-e72",
"apa_ref": "Pecher, D., van Mierlo, H., Cañal-Bruland, R., & Zeelenberg, R. (2015). The burden of secrecy? No effect on hill slant estimation and beanbag throwing. Journal of Experimental Psychology: General, 144(4), e65–e72. https://doi.org/10.1037/xge0000090",
"bibtex_ref": "@article{Pecher_2015, title={The burden of secrecy? No effect on hill slant estimation and beanbag throwing.}, volume={144}, ISSN={0096-3445}, url={http://dx.doi.org/10.1037/xge0000090}, DOI={10.1037/xge0000090}, number={4}, journal={Journal of Experimental Psychology: General}, publisher={American Psychological Association (APA)}, author={Pecher, Diane and van Mierlo, Heleen and Cañal-Bruland, Rouwen and Zeelenberg, René}, year={2015}, pages={e65–e72} }",
"url": null,
"outcome": "failed",
"abstract": null,
"outcome_quote": null
},
{
"doi": "10.3758/s13423-013-0549-2",
"doi_hash": "a04",
"rep_type": "replication",
"title": "Big secrets do not necessarily cause hills to appear steeper",
"authors": [
{
"given": "Etienne P.",
"family": "LeBel",
"sequence": "first"
},
{
"given": "Christopher J.",
"family": "Wilbur",
"sequence": "additional"
}
],
"journal": "Psychonomic Bulletin & Review",
"year": 2013,
"volume": "21.0",
"issue": "3",
"pages": "696-700",
"apa_ref": "LeBel, E. P., & Wilbur, C. J. (2013). Big secrets do not necessarily cause hills to appear steeper. Psychonomic Bulletin & Review, 21(3), 696–700. https://doi.org/10.3758/s13423-013-0549-2",
"bibtex_ref": "@article{LeBel_2013, title={Big secrets do not necessarily cause hills to appear steeper}, volume={21}, ISSN={1531-5320}, url={http://dx.doi.org/10.3758/s13423-013-0549-2}, DOI={10.3758/s13423-013-0549-2}, number={3}, journal={Psychonomic Bulletin & Review}, publisher={Springer Science and Business Media LLC}, author={LeBel, Etienne P. and Wilbur, Christopher J.}, year={2013}, month=nov, pages={696–700} }",
"url": null,
"outcome": "failed",
"abstract": null,
"outcome_quote": null
}
],
"originals": [],
"reproductions": []
}
}
}
}
```

---

## Response Model

### Top-level

* `results` is always present
* Missing items are returned as:

  * `[]` in prefix lookup
  * `null` in DOI lookup

### DOI record fields (stored in `DOI_TABLE.record`)

Each DOI record contains:

* DOI metadata:

  * `doi`, `doi_hash`, `title`, `authors`, `journal`, `year`, `volume`, `issue`, `pages`, `apa_ref`, `bibtex_ref`, `url`
* Relationships (under `record`):

  * `record.replications[]` 
  * `record.originals[]` 
  * `record.reproductions[]` 
* Stats:

  * counts for totals and unique DOI counts, plus reproduction totals

---

## Headers

| Header                        | Value                  | Notes            |
| ----------------------------- | ---------------------- | ---------------- |
| `Content-Type`                | `application/json`     | JSON in/out      |
| `Access-Control-Allow-Origin` | `*`                    | CORS             |
| `Cache-Control`               | `public, max-age=3600` | cacheable 1 hour |

---

## Error Responses

| Status | Meaning                 | Example                                                             |
| ------ | ----------------------- | ------------------------------------------------------------------- |
| `400`  | Missing query input     | `{"error":"No prefixes provided"}` / `{"error":"No DOIs provided"}` |
| `500`  | Server / DynamoDB error | `{"error":"Internal Server Error"}`                                 |

---

## Testing Snippets

### Windows (PowerShell)

```powershell
Invoke-RestMethod "https://rep-api.forrt.org/v1/prefix-lookup?prefixes=198" | ConvertTo-Json -Depth 10
```

### macOS/Linux

```bash
curl -s "https://rep-api.forrt.org/v1/original-lookup?dois=10.1037/a0027598" | jq .
```

### JavaScript (Node)

```js
const res = await fetch("https://rep-api.forrt.org/v1/original-lookup", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ dois: ["10.1037/a0027598"] }),
});
console.log(await res.json());
```

---

## Functions & Source

| Function         | Source            | Purpose                                       |
| ---------------- | ----------------- | --------------------------------------------- |
| `prefixLookup`   | `src/handler.ts`  | prefix → list of DOIs → batch-get DOI records |
| `originalLookup` | `src/original.ts` | DOI(s) → batch-get DOI records                |

---

## Notes

* Prefix lookups are **privacy-preserving**: clients only send **3-character hash prefixes**.
* Prefix table indexes **both doi_o_hash and doi_r_hash**, enabling the same endpoint to work for searching replication-side hashes too.
* `volume`, `issue`, and `pages` are always stored as **strings** (or `null`) for consistent output.
