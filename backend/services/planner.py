import re


def create_plan(query: str) -> dict:
    text = query.lower().strip()

    plan = {
        "intent": "data_search",
        "keywords": [],
        "remote": False,
        "days": None,
        "source_type": "jobs"
    }

    if any(word in text for word in [
        "job",
        "jobs",
        "developer",
        "role",
        "vacancy",
        "vacancies",
        "employment"
    ]):
        plan["intent"] = "job_search"

    if "remote" in text:
        plan["remote"] = True

    day_match = re.search(
        r"(?:last|past|previous)\s+(\d+)\s+days?",
        text
    )

    if day_match:
        plan["days"] = int(day_match.group(1))

    stop_words = {
        "find",
        "me",
        "the",
        "a",
        "an",
        "in",
        "for",
        "last",
        "past",
        "previous",
        "days",
        "day",
        "remote",
        "jobs",
        "job",
        "developer",
        "posted"
    }

    words = re.findall(r"[a-zA-Z0-9+#.]+", text)

    keywords = [
        word
        for word in words
        if word not in stop_words and len(word) > 1
    ]

    plan["keywords"] = keywords

    return plan