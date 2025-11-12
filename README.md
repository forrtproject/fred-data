# 🔍 FORRT Replication Database — Lightweight API

The backend for the **FORRT Replication Database (lightweight version)** is live and ready for testing.  
Query the database of replications either via **privacy-preserving 3-character DOI hash prefixes** or by **full original DOIs**.

> This API powers the **Zotero Replication Checker** plugin, connecting Zotero items to replication data from the FReD database.

**Base URL**
We have two separate APIs with two different URLs, one serves a Primary, and the URL is(Dev1) : 

```
https://rep-api.forrt.org/v1
```
The test API URL is(Dev0) :
```
https://80zw14hxjc.execute-api.eu-central-1.amazonaws.com
```
---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Endpoints](#endpoints)
  - [1) Prefix Lookup (privacy-preserving)](#1-prefix-lookup-privacy-preserving)
  - [2) Original DOI Lookup (direct)](#2-original-doi-lookup-direct)
- [Headers](#headers)
- [Error Responses](#error-responses)
- [Data Model](#data-model)
- [Testing Snippets](#testing-snippets)
- [Functions & Source](#functions--source)
- [Notes](#notes)

---

## Overview

- **Two lookup modes**
  1. **Prefix Lookup** — search by 3-character hash prefixes of DOIs (privacy-first).
  2. **Original DOI Lookup** — search by the full original DOI.
- **CORS enabled** and **cacheable** responses.

---

## Quick Start

**Check a hash prefix (GET)**
---
The "198" is a real hash prefix, and the "30e" does not exist in the database so that we could monitor the API's behaviour.
The Primary API:
```bash
curl "https://rep-api.forrt.org/v1/prefix-lookup?prefixes=198,30e"
```
The test API:
```bash
curl " https://80zw14hxjc.execute-api.eu-central-1.amazonaws.com/v1/prefix-lookup?prefixes=198,30e"
```
---

**Lookup by full DOI (GET)**

The "10.1037/a0027598" is a real DOI, and the "10.1016/j.jesp.2015.04.004" does not exist in the database so that we could monitor the API's behaviour.

The Primary API:
```bash
curl "https://rep-api.forrt.org/v1/original-lookup?doi=10.1016/j.jesp.2015.04.004,10.1037/a0027598"
```
The test API:
```bash
curl "https://iaq17d1dw6.execute-api.eu-central-1.amazonaws.com/v1/original-lookup?doi=10.1016/j.jesp.2015.04.004,10.1037/a0027598"
```
---

## Endpoints

### 1) Prefix Lookup (privacy-preserving)

Checks whether any **3-character hashed DOI prefixes** match replication families—without exposing full DOIs.

**URLs of Primary API**

| Method | URL                                                                |
| :----- | :----------------------------------------------------------------- |
| `POST` | `https://rep-api.forrt.org/v1/prefix-lookup`                       |
| `GET`  | `https://rep-api.forrt.org/v1/prefix-lookup?prefixes=198,30e`      |

**URLs of Test API**

| Method | URL                                                                |
| :----- | :----------------------------------------------------------------- |
| `POST` | ` https://80zw14hxjc.execute-api.eu-central-1.amazonaws.com/v1/prefix-lookup`                       |
| `GET`  | `https://80zw14hxjc.execute-api.eu-central-1.amazonaws.com/v1/prefix-lookup?prefixes=198,30e`      |

#### Example Requests

**POST of Primary API**

```bash
curl -X POST "https://rep-api.forrt.org/v1/prefix-lookup" \
  -H "Content-Type: application/json" \
  -d '{"prefixes":["198","30e"]}'
```
**POST  of Test API**

```bash
curl -X POST " https://80zw14hxjc.execute-api.eu-central-1.amazonaws.com/v1/prefix-lookup" \
  -H "Content-Type: application/json" \
  -d '{"prefixes":["198","30e"]}'
```

**GET  of Primary API**

```bash
curl "https://rep-api.forrt.org/v1/prefix-lookup?prefixes=198,30e"
```
**GET  of Test API**

```bash
curl " https://80zw14hxjc.execute-api.eu-central-1.amazonaws.com/v1/prefix-lookup?prefixes=198,30e"
```
#### Example Response — `200 OK`


```json
{
  "results": {
    "198": [
      {
        "hash_prefix": "198",
        "meta": {
          "original_doi": "10.1016/j.jesp.2015.04.004",
          "replications": [
            {
              "doi_r": "10.31234/osf.io/abcd1",
              "title_r": "Replication of Priming Effects",
              "author_r": [
                { "given": "Anna", "family": "Smith" },
                { "given": "Brian", "family": "Lopez" }
              ],
              "year_r": 2022,
              "outcome": "failure",
              "url_r": "https://osf.io/abcd1/"
            }
          ]
        }
      }
    ],
    "30e": []
  }
}
```

> **Tip:** Each top-level key under `results` (e.g., `"198"`, `"30e"`) corresponds to one requested prefix.

---

### 2) Original DOI Lookup (direct)

Fetch replication studies directly linked to a **full DOI** of an original publication.

**URLs of Primary API**

| Method | URL                                                                                         |
| :----- | :------------------------------------------------------------------------------------------ |
| `POST` | `https://rep-api.forrt.org/v1/original-lookup`                                              |
| `GET`  | `https://rep-api.forrt.org/v1/original-lookup?doi=10.1016/j.jesp.2015.04.004`              |

**URLs of Test API**

| Method | URL                                                                |
| :----- | :----------------------------------------------------------------- |
| `POST` | ` https://80zw14hxjc.execute-api.eu-central-1.amazonaws.com/v1/original-lookup`                       |
| `GET`  | `https://80zw14hxjc.execute-api.eu-central-1.amazonaws.com/v1/original-lookup?doi=10.1016/j.jesp.2015.04.004,10.1037/a0027598`      |


#### Example Requests

**POST of Primary API**

```bash
curl -X POST "https://rep-api.forrt.org/v1/original-lookup" \
  -H "Content-Type: application/json" \
  -d '{"dois": ["doi=10.1016/j.jesp.2015.04.004,10.1037/a0027598"]}'
```
**POST of Test API**

```bash
curl -X POST " https://80zw14hxjc.execute-api.eu-central-1.amazonaws.com/v1/original-lookup" \
  -H "Content-Type: application/json" \
  -d '{"dois": ["doi=10.1016/j.jesp.2015.04.004,10.1037/a0027598"]}'
```


**GET of Primary API**

```bash
curl "https://rep-api.forrt.org/v1/original-lookup?doi=10.1016/j.jesp.2015.04.004,10.1037/a0027598"
```
**GET of Test API**

```bash
curl "[https://80zw14hxjc.execute-api.eu-central-1.amazonaws.com/v1/original-lookup?doi=10.1016/j.jesp.2015.04.004,10.1037/a0027598"
```
#### Example Response — `200 OK`

```json
{
  "results": {
    "10.1016/j.jesp.2015.04.004": {
      "prefix": "198",
      "candidate": {
        "hash_prefix": "198",
        "meta": {
          "original_doi": "10.1016/j.jesp.2015.04.004",
          "replications": [
            {
              "doi_r": "10.31234/osf.io/abcd1",
              "title_r": "Replication of Priming Effects",
              "author_r": [
                { "given": "Anna", "family": "Smith" }
              ],
              "year_r": 2022,
              "outcome": "failure",
              "url_r": "https://osf.io/abcd1/"
            }
          ]
        }
      }
    }
  }
}
```

---

## Headers

| Header                        | Value                  | Notes                          |
| :---------------------------- | :--------------------- | :----------------------------- |
| `Content-Type`                | `application/json`     | JSON in/out                    |
| `Access-Control-Allow-Origin` | `*`                    | CORS enabled                   |
| `Cache-Control`               | `public, max-age=3600` | Responses cacheable for 1 hour |
| `X-Schema-Version`            | `2`                    | Response schema version        |

---

## Error Responses

**Prefix Lookup**

| Status | Description                    | Example                                   |
| :----- | :----------------------------- | :---------------------------------------- |
| `400`  | Missing or invalid prefix list | `{"error": "No prefixes provided"}`       |
| `500`  | DynamoDB / server error        | `{"error": "Internal Server Error"}`      |

**Original DOI Lookup**

| Status | Description         | Example                                                     |
| :----- | :------------------ | :---------------------------------------------------------- |
| `400`  | Missing DOI         | `{"error":"No DOIs provided"}`                              |
| `404`  | DOI not found       | `{"results":{"10.1016/j.abc.2020.1":[]}}`                   |
| `500`  | Internal error      | `{"error":"Internal Server Error"}`                         |

---

## Data Model

| Field                     | Type          | Description                                  |
| :------------------------ | :------------ | :------------------------------------------- |
| `hash_prefix`             | `string`      | 3-character hash of the original DOI         |
| `meta.original_doi`       | `string`      | Full DOI of the original study               |
| `meta.replications`       | `array`       | List of replication entries                  |
| `replications[].doi_r`    | `string`      | DOI of the replication                       |
| `replications[].title_r`  | `string`      | Title of the replication                     |
| `replications[].author_r` | `list/object` | Nested author data                           |
| `replications[].year_r`   | `number`      | Year of the replication                      |
| `replications[].outcome`  | `string`      | Replication result (e.g., `success/failure`) |
| `replications[].url_r`    | `string`      | Link to the replication resource             |

---

## Testing Snippets

**Windows (PowerShell)**

```powershell
Invoke-RestMethod "https://rep-api.forrt.org/v1/prefix-lookup?prefixes=198" | ConvertTo-Json -Depth 8
```

**macOS/Linux**

```bash
curl -s "https://rep-api.forrt.org/v1/prefix-lookup?prefixes=198" | jq .
```

**JavaScript (Node)**

```javascript
const res = await fetch("https://rep-api.forrt.org/v1/original-lookup", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ dois: ["10.1016/j.jesp.2015.04.004"] }),
});
console.log(await res.json());
```

---

## Functions & Source

| Function         | Source            | Purpose                                           | DynamoDB Table                        |
| :--------------- | :---------------- | :------------------------------------------------ | :------------------------------------ |
| `prefixLookup`   | `src/handler.ts`  | Looks up replication families via prefix hashes   | `zotero-replication-backend-prefix`   |
| `originalLookup` | `src/original.ts` | Looks up replication families via original DOIs   | `zotero-replication-backend-original` |

---

## Notes

- Each response for prefix lookups groups results by the **requested prefix** key.
- The `replications` array includes **all replication studies** for that family as loaded from the FReD CSV (all preserved columns except internal references).
