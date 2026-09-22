import requests
from datetime import datetime, timedelta, timezone


JOBICY_API = "https://jobicy.com/api/v2/remote-jobs"


def collect_jobs(keywords=None, days=None, limit=20):
    keywords = keywords or []

    params = {
        "count": limit
    }

    if keywords:
        params["tag"] = keywords[0]

    response = requests.get(
        JOBICY_API,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    jobs = data.get("jobs", [])

    cutoff = None

    if days:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    results = []
    seen = set()

    for job in jobs:

        title = job.get("jobTitle", "").strip()
        company = job.get("companyName", "").strip()
        url = job.get("url", "").strip()
        published = job.get("pubDate")

        if not title or not url:
            continue

        if url in seen:
            continue

        if cutoff and published:
            try:
                published_date = datetime.fromisoformat(
                    published.replace("Z", "+00:00")
                )

                if published_date < cutoff:
                    continue

            except ValueError:
                pass

        seen.add(url)

        results.append({
            "title": title,
            "company": company,
            "location": job.get("jobGeo", ""),
            "job_type": job.get("jobType", []),
            "level": job.get("jobLevel", ""),
            "description": job.get("jobExcerpt", ""),
            "url": url,
            "published": published,
            "source": "Jobicy"
        })

    return results