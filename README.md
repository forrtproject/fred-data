## 🔍 FORRT Replication Database (Lightweight Version)

The backend for the **FORRT Replication Database (lightweight version)** is now live again — and ready for more testing! 🎉  
You can query our database of replications either by **3-character DOI hash prefixes** (privacy-first) or by **full original DOIs**

Base URL

https://rep-api.forrt.org/v1


This API powers the Zotero Replication Checker Plugin — it connects Zotero items to replication data from the FReD database.

There are two lookup modes:

Prefix Lookup (privacy-preserving hash search)

Original DOI Lookup (direct search by full DOI)

🔹 1️⃣ Prefix Lookup
📍 Endpoint
Method	URL
POST	https://rep-api.forrt.org/v1/prefix-lookup
GET	https://rep-api.forrt.org/v1/prefix-lookup?prefixes=198,30e
🧭 Purpose

Checks whether any hashed DOI prefixes (3-character hashes) match replication families in the database — without exposing full DOIs.

📨 Example Request

POST

curl -X POST "https://rep-api.forrt.org/v1/prefix-lookup" \
  -H "Content-Type: application/json" \
  -d '{"prefixes":["198","30e"]}'


GET

curl "https://rep-api.forrt.org/v1/prefix-lookup?prefixes=198,30e"

✅ Example Response (200 OK)
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
                {"given": "Anna", "family": "Smith"},
                {"given": "Brian", "family": "Lopez"}
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


🧩 Notes

Each key ("198", "30e") represents one prefix.

Each replications array includes all replication studies for that prefix.

Data matches what was loaded from the FReD CSV (all preserved columns except internal refs).

⚙️ Headers
Header	Value
Content-Type	application/json
Access-Control-Allow-Origin	*
Cache-Control	public, max-age=3600
X-Schema-Version	2
❌ Error Responses
Status	Description	Example
400	Missing or invalid prefix list	{"error": "No prefixes provided"}
500	DynamoDB / server error	{"error": "Internal Server Error"}
🔹 2️⃣ Original DOI Lookup
📍 Endpoint
Method	URL
POST	https://rep-api.forrt.org/v1/original-lookup
GET	https://rep-api.forrt.org/v1/original-lookup?doi=10.1016/j.jesp.2015.04.004
🧭 Purpose

Fetch replication studies directly linked to a full DOI of an original publication.

📨 Example Request

POST

curl -X POST "https://rep-api.forrt.org/v1/original-lookup" \
  -H "Content-Type: application/json" \
  -d '{"dois": ["10.1016/j.jesp.2015.04.004"]}'


GET

https://rep-api.forrt.org/v1/original-lookup?doi=10.1016/j.jesp.2015.04.004

✅ Example Response
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
                {"given": "Anna", "family": "Smith"}
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

⚙️ Headers
Header	Value
Content-Type	application/json
Access-Control-Allow-Origin	*
Cache-Control	public, max-age=3600
❌ Error Responses
Status	Description	Example
400	Missing DOI	{"error":"No DOIs provided"}
404	DOI not found	{"results":{"10.1016/j.abc.2020.1":[]}}
500	Internal Server Error	{"error":"Internal Server Error"}
🧱 Data Model
Field	Type	Description
hash_prefix	string	3-character hash of the original DOI
meta.original_doi	string	Full DOI of the original study
meta.replications	array	List of replication entries
replications[].doi_r	string	DOI of replication
replications[].title_r	string	Title of the replication
replications[].author_r	list/object	Nested JSON of author data
replications[].year_r	number	Year of replication
replications[].outcome	string	Replication result
replications[].url_r	string	Link to the replication resource
⚡ Testing Snippets

Windows (PowerShell)

Invoke-RestMethod "https://rep-api.forrt.org/v1/prefix-lookup?prefixes=198" | ConvertTo-Json -Depth 8


macOS/Linux

curl -s "https://rep-api.forrt.org/v1/prefix-lookup?prefixes=198" | jq .


JavaScript (Node)

const res = await fetch("https://rep-api.forrt.org/v1/original-lookup", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ dois: ["10.1016/j.jesp.2015.04.004"] })
});
console.log(await res.json());

🧩 Functions
Function	Source	Purpose	DynamoDB Table
prefixLookup	src/handler.ts	Looks up replication families via prefix hashes	zotero-replication-backend-prefix
originalLookup	src/original.ts	Looks up replication families via original DOIs	zotero-replication-backend-original
