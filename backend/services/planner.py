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
    "internships",
    "trainee",
    "architect",
    "consultant",
    "administrator",
    "devops",
    "tester",
    "testing",
    "qa"
}


ROLE_NORMALIZATION = {
    "internships": "intern",
    "internship": "intern",
    "trainee": "intern",
    "developers": "developer",
    "engineers": "engineer",
    "designers": "designer",
    "analysts": "analyst",
    "scientists": "scientist",
    "managers": "manager",
    "architects": "architect",
    "consultants": "consultant",
    "administrators": "administrator",
    "testers": "tester"
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

    if any(word in text for word in [
        "job",
        "jobs",
        "developer",
        "developers",
        "role",
        "vacancy",
        "vacancies",
        "employment",
        "engineer",
        "engineers",
        "intern",
        "internship",
        "internships"
    ]):
        plan["intent"] = "job_search"

    if "remote" in text:
        plan["remote"] = True

    day_match = re.search(
        r"(?:last|past|previous|within)\s+(\d+)\s+days?",
        text
    )

    if day_match:
        plan["days"] = int(day_match.group(1))

    words = re.findall(
        r"[a-zA-Z0-9+#.]+",
        text
    )

    normalized_words = []

    for word in words:
        normalized_words.append(
            ROLE_NORMALIZATION.get(word, word)
        )

    for word in normalized_words:
        if word in ROLE_KEYWORDS:
            plan["role"].append(word)

    plan["role"] = list(
        dict.fromkeys(plan["role"])
    )

    keywords = []

    for original_word, normalized_word in zip(
        words,
        normalized_words
    ):
        if original_word in STOP_WORDS:
            continue

        if normalized_word in ROLE_KEYWORDS:
            continue

        if original_word.isdigit():
            continue

        if len(original_word) <= 1:
            continue

        keywords.append(original_word)

    plan["keywords"] = list(
        dict.fromkeys(keywords)
    )

    return plan