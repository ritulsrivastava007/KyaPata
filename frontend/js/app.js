const API_URL = "http://127.0.0.1:8000";

function getResultsContainer() {
    return document.getElementById("results");
}

function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function formatDate(value) {
    if (!value) {
        return "Recently posted";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "Recently posted";
    }

    return date.toLocaleDateString("en-US", {
        day: "numeric",
        month: "short",
        year: "numeric"
    });
}

function formatJobType(value) {
    if (Array.isArray(value)) {
        return value.join(" · ");
    }

    if (!value) {
        return "Any";
    }

    return String(value);
}

function renderResults(results, query, plan) {
    const container = getResultsContainer();

    if (!container) {
        return;
    }

    if (!results || results.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-title">
                    No matching results found
                </div>

                <div class="empty-text">
                    Try changing your search or using broader keywords.
                </div>
            </div>
        `;

        return;
    }

    const planTags = [];

    if (plan?.intent === "job_search") {
        planTags.push("Job search");
    }

    if (plan?.remote) {
        planTags.push("Remote");
    }

    if (plan?.keywords?.length) {
        planTags.push(
            ...plan.keywords
                .filter((keyword) => keyword.length > 1)
                .slice(0, 3)
                .map(
                    (keyword) =>
                        keyword.charAt(0).toUpperCase() +
                        keyword.slice(1)
                )
        );
    }

    if (plan?.days) {
        planTags.push(`Last ${plan.days} days`);
    }

    const cards = results.map((job) => {

        const reasons = Array.isArray(job.match_reasons)
            ? job.match_reasons
            : [];

        const fallbackReasons = [];

        if (plan?.keywords?.length) {
            const keyword = plan.keywords[0];

            fallbackReasons.push(
                `${keyword.charAt(0).toUpperCase() + keyword.slice(1)} matched`
            );
        }

        if (plan?.role?.length) {
            const role = plan.role[0];

            if (role === "developer") {
                fallbackReasons.push(
                    "Developer / Engineer role"
                );
            } else if (role === "engineer") {
                fallbackReasons.push(
                    "Engineer / Developer role"
                );
            } else {
                fallbackReasons.push(
                    `${role.charAt(0).toUpperCase() + role.slice(1)} role`
                );
            }
        }

        if (plan?.remote) {
            fallbackReasons.push(
                "Remote opportunity"
            );
        }

        if (plan?.days) {
            fallbackReasons.push(
                `Posted within ${plan.days} days`
            );
        }

        const displayReasons =
            reasons.length > 0
                ? reasons
                : fallbackReasons;

        const reasonMarkup = displayReasons.length
            ? `
                <div class="match-section">
                    <div class="match-label">
                        WHY THIS MATCHED
                    </div>

                    <div class="match-reasons">
                        ${displayReasons.map((reason) => `
                            <span class="match-reason">
                                <span class="match-check">✓</span>
                                ${escapeHtml(reason)}
                            </span>
                        `).join("")}
                    </div>
                </div>
            `
            : "";

        return `
            <article class="job-card">

                <div class="job-source">
                    ${escapeHtml(job.source || "Live source")}
                </div>

                <div class="job-card-main">

                    <div class="job-card-content">

                        <h3 class="job-title">
                            ${escapeHtml(job.title)}
                        </h3>

                        <div class="job-company">
                            ${escapeHtml(job.company || "Company")}
                        </div>

                        <div class="job-meta">

                            <span>
                                📍
                                ${escapeHtml(
                                    job.location || "Remote"
                                )}
                            </span>

                            <span>
                                ◉
                                ${escapeHtml(
                                    formatJobType(job.job_type)
                                )}
                            </span>

                            <span>
                                🕒
                                ${escapeHtml(
                                    formatDate(job.published)
                                )}
                            </span>

                        </div>

                        ${reasonMarkup}

                        <p class="job-description">
                            ${escapeHtml(
                                job.description || ""
                            )}
                        </p>

                        <a
                            class="job-link"
                            href="${escapeHtml(job.url)}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            View opportunity ↗
                        </a>

                    </div>

                </div>

            </article>
        `;
    }).join("");

    container.innerHTML = `
        <div class="understood-card">

            <div class="understood-label">
                UNDERSTOOD YOUR REQUEST
            </div>

            <div class="understood-content">

                <div class="understood-title">
                    KyaPata created a discovery plan
                </div>

                <div class="plan-tags">
                    ${planTags.map((tag) => `
                        <span class="plan-tag">
                            ${escapeHtml(tag)}
                        </span>
                    `).join("")}
                </div>

            </div>

        </div>

        <div class="results-header">

            <div>
                <div class="results-count">
                    ${results.length} opportunities found
                </div>

                <div class="results-query">
                    Results for
                    <strong>
                        "${escapeHtml(query)}"
                    </strong>
                </div>
            </div>

            <div class="live-indicator">
                <span class="live-dot"></span>
                Live data ✓
            </div>

        </div>

        <div class="results-list">
            ${cards}
        </div>
    `;
}

async function runQuery(query) {
    const container = getResultsContainer();

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="loading-state">

            <div class="loading-title">
                Understanding your request...
            </div>

            <div class="loading-text">
                KyaPata is searching live sources.
            </div>

        </div>
    `;

    try {
        const response = await fetch(
            `${API_URL}/api/query`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    query: query
                })
            }
        );

        if (!response.ok) {
            throw new Error(
                `Request failed: ${response.status}`
            );
        }

        const data = await response.json();

        if (!data.success) {
            container.innerHTML = `
                <div class="empty-state">

                    <div class="empty-title">
                        Something went wrong
                    </div>

                    <div class="empty-text">
                        ${escapeHtml(
                            data.message ||
                            "Unable to process your request."
                        )}
                    </div>

                </div>
            `;

            return;
        }

        renderResults(
            data.results,
            query,
            data.plan
        );

    } catch (error) {
        console.error(error);

        container.innerHTML = `
            <div class="empty-state">

                <div class="empty-title">
                    Unable to reach KyaPata
                </div>

                <div class="empty-text">
                    Make sure the backend server is running
                    on port 8000.
                </div>

            </div>
        `;
    }
}

function setupSearch() {

    const input = document.getElementById("queryInput");
    const button = document.getElementById("findButton");

    if (!input || !button) {
        console.error("KyaPata search elements not found.");
        return;
    }

    button.addEventListener("click", () => {

        const query = input.value.trim();

        if (!query) {
            input.focus();
            return;
        }

        runQuery(query);
    });

    input.addEventListener("keydown", (event) => {

        if (event.key === "Enter" && !event.shiftKey) {

            event.preventDefault();

            const query = input.value.trim();

            if (!query) {
                input.focus();
                return;
            }

            runQuery(query);
        }
    });
}

document.addEventListener(
    "DOMContentLoaded",
    setupSearch
);