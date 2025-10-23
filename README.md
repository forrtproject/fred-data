## 🔍 FORRT Replication Database (Lightweight Version)

The backend for the **FORRT Replication Database (lightweight version)** is now live again — and ready for more testing! 🎉  
You can query our database of replications either by **3-character DOI hash prefixes** (privacy-first) or by **full original DOIs**.

---

### 🧩 Base URL
```
https://ouj1xoiypb.execute-api.eu-central-1.amazonaws.com
```

---

### 🔹 1️⃣ Prefix Lookup

Check replications using **3-character hash prefixes** (computed from DOIs).

#### POST
```bash
curl -X POST "https://ouj1xoiypb.execute-api.eu-central-1.amazonaws.com/v1/prefix-lookup"   -H "Content-Type: application/json"   -d '{"prefixes":["30e","92e"]}'
```

#### GET
```
https://ouj1xoiypb.execute-api.eu-central-1.amazonaws.com/v1/prefix-lookup?prefixes=30e,92e
```

Each prefix returns an array of replication families (original DOI + list of replications).

---

### 🔹 2️⃣ Original DOI Lookup

Look up replication families by **full original DOI**.

#### POST
```bash
curl -X POST "https://ouj1xoiypb.execute-api.eu-central-1.amazonaws.com/v1/original-lookup"   -H "Content-Type: application/json"   -d '{"dois":["10.1234/abcde.2020.001"]}'
```

#### GET
```
https://ouj1xoiypb.execute-api.eu-central-1.amazonaws.com/v1/original-lookup?doi=10.1234/abcde.2020.001
```

---

### 🧠 Works Everywhere

#### ✅ Windows PowerShell
```powershell
Invoke-RestMethod "https://ouj1xoiypb.execute-api.eu-central-1.amazonaws.com/v1/prefix-lookup?prefixes=30e,92e" | ConvertTo-Json -Depth 8
```

#### ✅ macOS / Linux
```bash
curl -s "https://ouj1xoiypb.execute-api.eu-central-1.amazonaws.com/v1/prefix-lookup?prefixes=30e,92e" | jq .
```

🎉

## Hashes

The 3-character DOI hash prefixes are computed using the first 3 characters of the md5 hash of the DOI string (in lowercase).

How to generate?

### JavaScript

```javascript
import CryptoJS from "crypto-js";

const doi = "10.1037/0022-3514.67.4.627";
const prefix = CryptoJS.MD5(doi).toString().slice(0, 3);
console.log(prefix);
```

### R 

```r
library(digest)
doi <- "10.1037/0022-3514.67.4.627"
prefix <- substr(digest(doi, algo = "md5", serialize = FALSE), 1, 3)
prefix
```

### Python

```python
import hashlib

doi = "10.1037/0022-3514.67.4.627"
prefix = hashlib.md5(doi.encode()).hexdigest()[:3]
print(prefix)


```


### Python
