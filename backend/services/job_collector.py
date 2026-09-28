import re
import html
import requests

from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser


JOBICY_API = "https://jobicy.com/api/v2/remote-jobs"
HIMALAYAS_API = "https://himalayas.app/jobs/api/search"


ROLE_SYNONYMS = {
    "developer": {
        "developer",
        "engineer",
        "software",
        "programmer",
        "development"
    },
    "engineer": {
        "engineer",
        "developer",
        "software",
        "programmer",
        "development"
    },
    "designer": {
        "designer",
        "design",
        "ux",
        "ui"
    },
    "analyst": {
        "analyst",
        "analysis"
    },
    "devops": {
        "devops",
        "devops engineer",
        "cloud engineer"
    },
    "tester": {
        "tester",
        "testing",
        "qa",
        "quality assurance"
    },
    "intern": {
        "intern",
        "internship",
        "internships",
        "trainee"
    }
}


SOURCE_SEARCH_TERMS = {
    "devops": [
        "devops",
        "devops engineer",
        "cloud engineer"
    ],
    "developer": [
        "developer",
        "software developer",
        "software engineer"
    ],
    "engineer": [
        "engineer",
        "software engineer",
        "developer"
    ],
    "designer": [
        "designer",
        "ux designer",
        "ui designer"
    ],
    "analyst": [
        "analyst",
        "data analyst"
    ],
    "tester": [
        "tester",
        "qa",
        "quality assurance"
    ],
    "intern": [
        "intern",
        "internship"
    ]
}


class HTMLTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"p", "div", "br", "li", "h1", "h2", "h3", "h4"}:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in {"p", "div", "li", "h1", "h2", "h3", "h4"}:
            self.parts.append(" ")

    def handle_data(self, data):
        self.parts.append(data)


def clean_html(text):
    if not text:
        return ""

    text = str(text)

    parser = HTMLTextParser()

    try:
        parser.feed(text)
        parser.close()
        text = "".join(parser.parts)
    except Exception:
        text = re.sub(r"<[^>]+>", " ", text)

    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def fetch_jobicy(params):
    try:
        response = requests.get(
            JOBICY_API,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):
            jobs = data.get("jobs", [])

            if isinstance(jobs, list):
                return jobs

        return []

    except (requests.RequestException, ValueError):
        return []


def fetch_himalayas(query, limit=20):
    try:
        response = requests.get(
            HIMALAYAS_API,
            params={
                "q": query,
                "sort": "recent",
                "page": 1
            },
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):
            jobs = data.get("jobs", [])

            if isinstance(jobs, list):
                return jobs[:limit]

        return []

    except (requests.RequestException, ValueError):
        return []


def parse_date(value):
    if value is None or value == "":
        return None

    try:
        if isinstance(value, (int, float)):
            timestamp = float(value)

            if timestamp < 10_000_000_000:
                return datetime.fromtimestamp(
                    timestamp,
                    tz=timezone.utc
                )

            if timestamp < 10_000_000_000_000:
                timestamp /= 1000

                return datetime.fromtimestamp(
                    timestamp,
                    tz=timezone.utc
                )

            timestamp /= 1_000_000

            return datetime.fromtimestamp(
                timestamp,
                tz=timezone.utc
            )

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return None

            if re.fullmatch(r"\d+(?:\.\d+)?", value):
                timestamp = float(value)

                if timestamp < 10_000_000_000:
                    return datetime.fromtimestamp(
                        timestamp,
                        tz=timezone.utc
                    )

                if timestamp < 10_000_000_000_000:
                    timestamp /= 1000

                    return datetime.fromtimestamp(
                        timestamp,
                        tz=timezone.utc
                    )

                timestamp /= 1_000_000

                return datetime.fromtimestamp(
                    timestamp,
                    tz=timezone.utc
                )

            try:
                parsed = datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                )

                if parsed.tzinfo is None:
                    parsed = parsed.replace(
                        tzinfo=timezone.utc
                    )

                return parsed.astimezone(timezone.utc)

            except ValueError:
                pass

            for fmt in [
                "%Y-%m-%d",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f"
            ]:
                try:
                    return datetime.strptime(
                        value,
                        fmt
                    ).replace(tzinfo=timezone.utc)

                except ValueError:
                    continue

    except (
        ValueError,
        OSError,
        OverflowError,
        TypeError
    ):
        return None

    return None


def get_source_queries(search_terms, role_terms):
    queries = []

    for term in role_terms:
        queries.extend(
            SOURCE_SEARCH_TERMS.get(
                term,
                [term]
            )
        )

    queries.extend(search_terms)

    return list(
        dict.fromkeys(
            query.strip().lower()
            for query in queries
            if query.strip()
        )
    )


def collect_jobs(
    keywords=None,
    role=None,
    days=None,
    limit=20
):
    keywords = keywords or []
    role = role or []

    search_terms = [
        str(keyword).strip().lower()
        for keyword in keywords
        if str(keyword).strip()
        and not str(keyword).strip().isdigit()
        and len(str(keyword).strip()) > 1
    ]

    role_terms = [
        str(item).strip().lower()
        for item in role
        if str(item).strip()
    ]

    expanded_roles = set()

    for item in role_terms:
        if item in ROLE_SYNONYMS:
            expanded_roles.update(
                ROLE_SYNONYMS[item]
            )
        else:
            expanded_roles.add(item)

    source_queries = get_source_queries(
        search_terms,
        role_terms
    )

    all_jobs = []

    # --------------------------------------------------
    # SOURCE 1: JOBICY
    # --------------------------------------------------

    jobicy_queries = source_queries or ["remote"]

    for source_query in jobicy_queries:
        try:
            jobicy_jobs = fetch_jobicy({
                "count": 200,
                "tag": source_query
            })

            for job in jobicy_jobs:
                title = str(
                    job.get("jobTitle", "") or ""
                ).strip()

                company = str(
                    job.get("companyName", "") or ""
                ).strip()

                description = str(
                    job.get("jobDescription", "") or ""
                ).strip()

                excerpt = str(
                    job.get("jobExcerpt", "") or ""
                ).strip()

                searchable = " ".join([
                    title,
                    company,
                    description,
                    excerpt
                ]).lower()

                all_jobs.append({
                    "title": title,
                    "company": company,
                    "location": job.get(
                        "jobGeo",
                        ""
                    ),
                    "job_type": job.get(
                        "jobType",
                        []
                    ),
                    "level": job.get(
                        "jobLevel",
                        ""
                    ),
                    "description": clean_html(
                        excerpt or description
                    ),
                    "url": str(
                        job.get("url", "") or ""
                    ).strip(),
                    "published": job.get(
                        "pubDate"
                    ),
                    "source": "Jobicy",
                    "_searchable": searchable
                })

        except (requests.RequestException, ValueError):
            continue

    # --------------------------------------------------
    # SOURCE 2: HIMALAYAS
    # --------------------------------------------------

    himalayas_queries = source_queries or [
        "remote jobs"
    ]

    for source_query in himalayas_queries:
        try:
            himalayas_jobs = fetch_himalayas(
                source_query,
                limit=limit
            )

            for job in himalayas_jobs:
                title = str(
                    job.get("title")
                    or job.get("name")
                    or ""
                ).strip()

                company_data = job.get(
                    "company",
                    ""
                )

                if isinstance(company_data, dict):
                    company = str(
                        company_data.get("name")
                        or ""
                    ).strip()
                else:
                    company = str(
                        company_data or ""
                    ).strip()

                description = str(
                    job.get("description")
                    or job.get("excerpt")
                    or ""
                ).strip()

                location = (
                    job.get("location")
                    or job.get("country")
                    or ""
                )

                url = str(
                    job.get("applicationLink")
                    or job.get("url")
                    or job.get("guid")
                    or ""
                ).strip()

                published = (
                    job.get("publishedAt")
                    or job.get("pubDate")
                    or job.get("createdAt")
                )

                clean_description = clean_html(
                    description
                )

                searchable = " ".join([
                    title,
                    company,
                    clean_description,
                    str(location)
                ]).lower()

                all_jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "job_type": (
                        job.get("employmentType")
                        or job.get("jobType")
                        or []
                    ),
                    "level": (
                        job.get("seniority")
                        or job.get("jobLevel")
                        or ""
                    ),
                    "description": clean_description,
                    "url": url,
                    "published": published,
                    "source": "Himalayas",
                    "_searchable": searchable
                })

        except (requests.RequestException, ValueError):
            continue

    # --------------------------------------------------
    # FILTER + RANK
    # --------------------------------------------------

    cutoff = None

    if days:
        cutoff = (
            datetime.now(timezone.utc)
            - timedelta(days=days)
        )

    results = []
    seen = set()

    for job in all_jobs:
        title = job["title"]
        url = job["url"]

        if not title or not url:
            continue

        normalized_url = url.lower().rstrip("/")

        if normalized_url in seen:
            continue

        searchable_text = job["_searchable"]
        title_lower = title.lower()

        # ----------------------------------------------
        # KEYWORD MATCHING
        # ----------------------------------------------

        matched_keywords = [
            keyword
            for keyword in search_terms
            if keyword in searchable_text
        ]

        if search_terms and not matched_keywords:
            continue

        # ----------------------------------------------
        # ROLE MATCHING
        # ----------------------------------------------

        matched_roles = [
            item
            for item in expanded_roles
            if item in title_lower
        ]

        if expanded_roles and not matched_roles:
            continue

        # ----------------------------------------------
        # DATE
        # ----------------------------------------------

        published_date = parse_date(
            job["published"]
        )

        if cutoff and published_date:
            if published_date < cutoff:
                continue

        # ----------------------------------------------
        # SCORE
        # ----------------------------------------------

        score = 0

        for keyword in matched_keywords:
            if keyword in title_lower:
                score += 6
            elif keyword in job["company"].lower():
                score += 3
            else:
                score += 1

        for role_item in matched_roles:
            if role_item in title_lower:
                score += 6
            else:
                score += 2

        if (
            matched_keywords
            and matched_roles
            and any(
                keyword in title_lower
                for keyword in matched_keywords
            )
            and any(
                role_item in title_lower
                for role_item in matched_roles
            )
        ):
            score += 5

        if published_date:
            age_hours = (
                datetime.now(timezone.utc)
                - published_date
            ).total_seconds() / 3600

            if age_hours <= 24:
                score += 3
            elif age_hours <= 72:
                score += 2

        # ----------------------------------------------
        # MATCH REASONS
        # ----------------------------------------------

        match_reasons = []

        for keyword in matched_keywords:
            label = keyword.capitalize()

            if keyword in title_lower:
                match_reasons.append(
                    f"{label} in title"
                )
            else:
                match_reasons.append(
                    f"{label} mentioned"
                )

        if matched_roles:
            primary_role = (
                role_terms[0]
                if role_terms
                else None
            )

            if primary_role == "developer":
                match_reasons.append(
                    "Developer / Engineer role"
                )

            elif primary_role == "engineer":
                match_reasons.append(
                    "Engineer / Developer role"
                )

            elif primary_role == "intern":
                match_reasons.append(
                    "Intern role"
                )

            elif primary_role == "devops":
                match_reasons.append(
                    "DevOps / Cloud role"
                )

            elif primary_role:
                match_reasons.append(
                    f"{primary_role.capitalize()} role"
                )

        if days and published_date:
            match_reasons.append(
                f"Posted within {days} days"
            )

        # ----------------------------------------------
        # FINALIZE
        # ----------------------------------------------

        job.pop("_searchable", None)

        if published_date:
            job["published"] = (
                published_date.isoformat()
            )

        job["relevance_score"] = score
        job["match_reasons"] = match_reasons

        seen.add(normalized_url)
        results.append(job)

    results.sort(
        key=lambda job: (
            job["relevance_score"],
            str(job.get("published") or "")
        ),
        reverse=True
    )

    return results[:limit]