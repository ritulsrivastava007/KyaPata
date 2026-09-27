import re


ROLE_KEYWORDS = {
    "developer",
    "engineer",
    "designer",
    "analyst",
    "scientist",
    "manager",
    "intern",
    "internship",
    "architect",
    "consultant",
    "administrator",
    "devops",
    "tester",
    "qa"
}


STOP_WORDS = {
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
    "posted",
    "within",
    "from",
    "show",
    "give",
    "looking",
    "look",
    "want",
    "need"
}


def create_plan(query: str) -> dict:

    text = query.lower().strip()


    plan = {
        "intent": "data_search",
        "keywords": [],
        "role": [],
        "remote": False,
        "days": None,
        "source_type": "jobs"
    }


    # --------------------------------
    # INTENT
    # --------------------------------

    if any(word in text for word in [
        "job",
        "jobs",
        "developer",
        "role",
        "vacancy",
        "vacancies",
        "employment",
        "engineer",
        "internship",
        "intern"
    ]):
        plan["intent"] = "job_search"


    # --------------------------------
    # REMOTE
    # --------------------------------

    if "remote" in text:
        plan["remote"] = True


    # --------------------------------
    # DATE RANGE
    # --------------------------------

    day_match = re.search(
        r"(?:last|past|previous|within)\s+(\d+)\s+days?",
        text
    )

    if day_match:
        plan["days"] = int(day_match.group(1))


    # --------------------------------
    # WORD EXTRACTION
    # --------------------------------

    words = re.findall(
        r"[a-zA-Z0-9+#.]+",
        text
    )


    # --------------------------------
    # ROLE EXTRACTION
    # --------------------------------

    for word in words:

        if word in ROLE_KEYWORDS:
            plan["role"].append(word)


    # Remove duplicate roles while preserving order.

    plan["role"] = list(
        dict.fromkeys(plan["role"])
    )


    # --------------------------------
    # GENERAL KEYWORDS
    # --------------------------------

    keywords = []

    for word in words:

        if word in STOP_WORDS:
            continue

        if word in ROLE_KEYWORDS:
            continue

        if word.isdigit():
            continue

        if len(word) <= 1:
            continue

        keywords.append(word)


    # Remove duplicates.

    plan["keywords"] = list(
        dict.fromkeys(keywords)
    )


    return plan