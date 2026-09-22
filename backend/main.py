from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.planner import create_plan
from services.job_collector import collect_jobs


app = FastAPI(
    title="KyaPata API",
    description="AI-powered data discovery platform",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str


@app.get("/")
def root():
    return {
        "name": "KyaPata",
        "status": "online",
        "message": "Ask. Find. Know."
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/api/query")
def process_query(request: QueryRequest):

    query = request.query.strip()

    if not query:
        return {
            "success": False,
            "message": "Please enter a query."
        }

    plan = create_plan(query)

    results = []

    if plan["intent"] == "job_search":
        results = collect_jobs(
            keywords=plan["keywords"],
            days=plan["days"],
            limit=20
        )

    return {
        "success": True,
        "query": query,
        "plan": plan,
        "results": results,
        "message": "Query processed successfully."
    }