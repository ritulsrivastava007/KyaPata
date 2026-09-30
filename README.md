# KyaPata

### Ask. Find. Know.

**KyaPata** is a natural-language data discovery platform that turns a question into a structured search workflow, collects information from permitted live sources, filters and ranks the results, and presents them with source traceability.

Instead of making users search multiple platforms manually, KyaPata lets them describe what they need in plain language.

> **Example:**
> `Find remote Python developer jobs posted in the last 7 days`

KyaPata interprets the request, identifies the search intent, applies relevant filters, collects live job data, and presents the results in one place.

---

## ✨ What KyaPata Does

KyaPata is designed around a simple workflow:

```text
Natural-language query
        ↓
Understand intent
        ↓
Create search plan
        ↓
Collect from permitted sources
        ↓
Filter + validate + deduplicate
        ↓
Rank relevant results
        ↓
Show results + source + match reasons
```

### Current MVP

The current MVP focuses on **remote job discovery**.

It supports queries involving:

* 💼 Job searches
* 👨‍💻 Developer / Engineer roles
* ☁️ DevOps / Cloud roles
* 🎨 Designer roles
* 📊 Analyst roles
* 🧪 Testing / QA roles
* 🎓 Internships
* 🌐 Remote opportunities
* 📅 Recent-posting filters
* 🔎 Keyword-based discovery

---

## 🚀 Why KyaPata?

Information is often available online but fragmented across different platforms.

A user may have to:

1. Decide where to search
2. Open multiple websites
3. Repeat the same query
4. Apply filters manually
5. Compare results
6. Verify where each result came from

KyaPata aims to reduce this friction by turning the user's question into a structured discovery workflow.

### Instead of:

> Search → Filter → Compare → Verify

### KyaPata aims for:

> **Ask → Find → Know**

---

## 🧠 How It Works

### 01 — You Ask

The user describes the information they need using natural language.

```text
Find remote DevOps jobs in the last 14 days
```

### 02 — KyaPata Plans

The request is converted into structured parameters such as:

```json
{
  "intent": "job_search",
  "role": ["devops"],
  "remote": true,
  "days": 14
}
```

### 03 — Data Is Collected

The backend queries permitted external job sources and normalizes their responses into a common structure.

### 04 — Results Are Filtered

KyaPata applies:

* Keyword matching
* Role matching
* Remote job discovery
* Date filtering
* Duplicate removal

### 05 — Results Are Ranked

Relevant title matches and role matches receive higher relevance scores.

### 06 — You Know

Results are presented with:

* Job title
* Company
* Location
* Job type
* Publication date
* Source
* Match reasons
* Original opportunity link

---

## 🔎 Source Transparency

KyaPata currently integrates live data from:

| Source        | Purpose              |
| ------------- | -------------------- |
| **Jobicy**    | Remote job discovery |
| **Himalayas** | Remote job discovery |

Results identify their originating source so users can understand where the information came from.

KyaPata does **not** claim to search the entire internet. The current MVP works with the permitted sources integrated into the application.

---

## 🏗️ Architecture

```text
┌──────────────────────────────┐
│          Frontend            │
│       HTML / CSS / JS        │
└──────────────┬───────────────┘
               │
               │ HTTP / JSON
               ▼
┌──────────────────────────────┐
│         FastAPI API          │
│        backend/main.py       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Query Planner          │
│     services/planner.py      │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Job Collector          │
│   services/job_collector.py  │
└──────────────┬───────────────┘
               │
          ┌────┴────┐
          ▼         ▼
       Jobicy   Himalayas
          │         │
          └────┬────┘
               ▼
       Filter / Rank / Deduplicate
               │
               ▼
          Results UI
```

---

## 🛠️ Tech Stack

### Frontend

* HTML5
* CSS3
* Vanilla JavaScript

### Backend

* Python
* FastAPI
* Pydantic
* Requests

### Data Sources

* Jobicy API
* Himalayas Jobs API

### Development

* Git
* GitHub
* VS Code / any Python-compatible editor

---

## 📁 Project Structure

```text
KyaPata/
│
├── backend/
│   ├── main.py
│   └── services/
│       ├── __init__.py
│       ├── planner.py
│       └── job_collector.py
│
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── main.css
│   └── js/
│       └── app.js
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## ⚡ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ritulsrivastava007/KyaPata.git
cd KyaPata
```

### 2. Set up the backend

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install fastapi uvicorn requests python-dotenv
```

### 3. Start the backend

```bash
cd backend
python -m uvicorn main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

### 4. Start the frontend

Open another terminal:

```bash
cd frontend
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500
```

---

## 🔌 API

### Health Check

```http
GET /api/health
```

Example response:

```json
{
  "status": "healthy"
}
```

### Query

```http
POST /api/query
```

Request:

```json
{
  "query": "find remote python developer jobs in last 7 days"
}
```

The response contains the interpreted plan and collected results.

---

## 🧪 Example Queries

Try:

```text
find remote python developer jobs in last 7 days
```

```text
find remote javascript developer jobs in last 7 days
```

```text
find remote devops jobs in last 14 days
```

```text
find remote internships
```

```text
find remote designer jobs
```

The results include source information and explanations for why an opportunity matched the query.

---

## 📌 Current MVP Limitations

KyaPata is currently an MVP focused on job discovery.

Current limitations include:

* The available results depend on the integrated external sources.
* It does not search the entire web.
* The current planner uses structured rule-based intent extraction.
* Job availability and freshness depend on the external APIs.
* The current frontend is intended for local/demo use.
* Additional domains beyond job discovery are planned but are not part of the current MVP.

These constraints are intentional so the current prototype remains focused and demonstrable.

---

## 🗺️ Roadmap

### Phase 1 — Current MVP

* [x] Natural-language job queries
* [x] Query planning
* [x] Live external data
* [x] Multiple job sources
* [x] Keyword and role matching
* [x] Date filtering
* [x] Remote job discovery
* [x] Deduplication
* [x] Relevance ranking
* [x] Match explanations
* [x] Source transparency
* [x] Search history

### Phase 2 — Expansion

* [ ] More permitted data sources
* [ ] More discovery domains
* [ ] Better semantic query understanding
* [ ] Advanced result ranking
* [ ] Saved searches
* [ ] Result export
* [ ] User-configurable search workflows

### Phase 3 — Platform

* [ ] Pluggable source connectors
* [ ] More sophisticated planning
* [ ] Cross-source normalization
* [ ] Advanced provenance and validation
* [ ] Hosted deployment

---

## 🎯 Project Vision

KyaPata is built around a simple idea:

> **The user should describe what they need, not figure out where and how to search for it.**

The long-term goal is to build a general-purpose discovery layer that can transform natural-language information needs into transparent, reproducible data workflows.

---

## 🎥 Demo

▶️ [Watch the KyaPata Demo](https://youtu.be/CsSfP30yO5Q)

See KyaPata turn natural-language queries into live, traceable job-discovery results.

---

## 🤝 Contributing

Contributions, suggestions, and ideas are welcome.

If you find a bug or have an idea for improving KyaPata, open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the **MIT License**.

See [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

**Ritul Srivastava**

Computer Engineering Student

* GitHub: [@ritulsrivastava007](https://github.com/ritulsrivastava007)
* LeetCode: [ritul_07](https://leetcode.com/u/ritul_07)

---

<p align="center">
  <strong>KyaPata</strong><br>
  Ask. Find. Know.
</p>
