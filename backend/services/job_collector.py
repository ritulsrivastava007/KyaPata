import requests
from datetime import datetime, timedelta, timezone


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
        "trainee"
    }
}


def fetch_jobicy(params):
    response = requests.get(
        JOBICY_API,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json().get("jobs", [])


def fetch_himalayas(query, limit=20):
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
        return data.get("jobs", [])

    return []


def parse_date(value):

    if not value:
        return None

    if isinstance(value, (int, float)):

        try:
            return datetime.fromtimestamp(
                value / 1000,
                tz=timezone.utc
            )
        except (ValueError, OSError, OverflowError):
            return None

    if isinstance(value, str):

        value = value.strip()

        if value.isdigit():

            try:
                return datetime.fromtimestamp(
                    int(value) / 1000,
                    tz=timezone.utc
                )
            except (ValueError, OSError, OverflowError):
                return None

        try:
            return datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError:
            pass

        for fmt in [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S"
        ]:

            try:
                return datetime.strptime(
                    value,
                    fmt
                ).replace(tzinfo=timezone.utc)

            except ValueError:
                continue

    return None


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

    all_jobs = []

    # --------------------------------------------------
    # SOURCE 1: JOBICY
    # --------------------------------------------------

    try:

        params = {
            "count": 200
        }

        if search_terms:
            params["tag"] = search_terms[0]

        jobicy_jobs = fetch_jobicy(params)

        for job in jobicy_jobs:

            title = job.get(
                "jobTitle",
                ""
            ).strip()

            company = job.get(
                "companyName",
                ""
            ).strip()

            description = job.get(
                "jobDescription",
                ""
            ).strip()

            excerpt = job.get(
                "jobExcerpt",
                ""
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
                "description": excerpt or description,
                "url": job.get(
                    "url",
                    ""
                ).strip(),
                "published": job.get(
                    "pubDate"
                ),
                "source": "Jobicy",
                "_searchable": searchable
            })

    except requests.RequestException:
        pass

    # --------------------------------------------------
    # SOURCE 2: HIMALAYAS
    # --------------------------------------------------

    try:

        query_parts = []

        query_parts.extend(search_terms)
        query_parts.extend(role_terms)

        himalayas_query = " ".join(
            dict.fromkeys(query_parts)
        ).strip()

        if not himalayas_query:
            himalayas_query = "remote jobs"

        himalayas_jobs = fetch_himalayas(
            himalayas_query,
            limit=limit
        )

        for job in himalayas_jobs:

            title = (
                job.get("title")
                or job.get("name")
                or ""
            ).strip()

            company_data = job.get(
                "company",
                ""
            )

            if isinstance(company_data, dict):

                company = (
                    company_data.get("name")
                    or ""
                ).strip()

            else:

                company = str(
                    company_data or ""
                ).strip()

            description = (
                job.get("description")
                or job.get("excerpt")
                or ""
            ).strip()

            location = (
                job.get("location")
                or job.get("country")
                or ""
            )

            url = (
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

            searchable = " ".join([
                title,
                company,
                description,
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
                "description": description,
                "url": url,
                "published": published,
                "source": "Himalayas",
                "_searchable": searchable
            })

    except requests.RequestException:
        pass

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

        matched_keywords = [
            keyword
            for keyword in search_terms
            if keyword in searchable_text
        ]

        if search_terms and not matched_keywords:
            continue

        matched_roles = [
            item
            for item in expanded_roles
            if item in title_lower
        ]

        if expanded_roles and not matched_roles:
            continue

        published_date = parse_date(
            job["published"]
        )

        if cutoff and published_date:

            if published_date < cutoff:
                continue

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

            primary_role = role_terms[0] if role_terms else None

            if primary_role:

                if primary_role == "developer":
                    match_reasons.append(
                        "Developer / Engineer role"
                    )

                elif primary_role == "engineer":
                    match_reasons.append(
                        "Engineer / Developer role"
                    )

                else:
                    match_reasons.append(
                        f"{primary_role.capitalize()} role"
                    )

        if days:

            if published_date:

                match_reasons.append(
                    f"Posted within {days} days"
                )

        job.pop("_searchable", None)

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