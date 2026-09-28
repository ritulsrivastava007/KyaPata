const API_URL = "http://127.0.0.1:8000";

function getResultsContainer() {
    return document.getElementById("results");
}

function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    const text = String(value);

    const textarea = document.createElement("textarea");
    textarea.innerHTML = text;

    return textarea.value
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

    const sourceCounts = {};

    results.forEach((job) => {
        const source = job.source || "Unknown source";

        sourceCounts[source] =
            (sourceCounts[source] || 0) + 1;
    });

    const sourceSummary = Object.entries(sourceCounts)
        .map(([source, count]) => `
            <span class="source-summary-item">
                <strong>${count}</strong>
                ${escapeHtml(source)}
            </span>
        `)
        .join("");

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

            <div class="results-live-info">

                <div class="live-indicator">
                    <span class="live-dot"></span>
                    Live data ✓
                </div>

                <div class="source-summary">
                    ${sourceSummary}
                </div>

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

        saveSearchHistory(
            query,
            data.results ? data.results.length : 0
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

function saveSearchHistory(query, resultCount) {
    const history = JSON.parse(
        localStorage.getItem("kyapata_history") || "[]"
    );

    const entry = {
        query: query,
        resultCount: resultCount,
        timestamp: new Date().toISOString()
    };

    const filteredHistory = history.filter(
        (item) =>
            item.query.toLowerCase() !== query.toLowerCase()
    );

    filteredHistory.unshift(entry);

    localStorage.setItem(
        "kyapata_history",
        JSON.stringify(filteredHistory.slice(0, 10))
    );
}

function getSearchHistory() {
    return JSON.parse(
        localStorage.getItem("kyapata_history") || "[]"
    );
}

function renderHistory() {
    const container = getResultsContainer();

    if (!container) {
        return;
    }

    const history = getSearchHistory();

    if (history.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-title">
                    No search history yet
                </div>

                <div class="empty-text">
                    Your previous KyaPata searches will appear here.
                </div>
            </div>
        `;

        return;
    }

    const items = history.map((item) => {
        const date = new Date(item.timestamp);

        const formattedDate = date.toLocaleString("en-US", {
            day: "numeric",
            month: "short",
            year: "numeric",
            hour: "numeric",
            minute: "2-digit"
        });

        return `
            <button
                class="history-item"
                data-query="${escapeHtml(item.query)}"
            >
                <div class="history-item-main">
                    <div class="history-query">
                        ${escapeHtml(item.query)}
                    </div>

                    <div class="history-meta">
                        ${formattedDate}
                        ·
                        ${item.resultCount} results
                    </div>
                </div>

                <span class="history-arrow">→</span>
            </button>
        `;
    }).join("");

    container.innerHTML = `
        <div class="results-header">
            <div>
                <div class="results-count">
                    Search history
                </div>

                <div class="results-query">
                    Your recent KyaPata discoveries
                </div>
            </div>
        </div>

        <div class="history-list">
            ${items}
        </div>
    `;

    container
        .querySelectorAll(".history-item")
        .forEach((item) => {
            item.addEventListener("click", () => {
                const query = item.dataset.query;

                document.getElementById("queryInput").value = query;

                setActiveNav("discover");

                runQuery(query);
            });
        });
}

function setActiveNav(active) {
    const discoverLink =
        document.getElementById("discoverLink");

    const historyLink =
        document.getElementById("historyLink");

    if (!discoverLink || !historyLink) {
        return;
    }

    discoverLink.classList.toggle(
        "active",
        active === "discover"
    );

    historyLink.classList.toggle(
        "active",
        active === "history"
    );
}

function setupHistory() {
    const historyLink =
        document.getElementById("historyLink");

    const discoverLink =
        document.getElementById("discoverLink");

    if (!historyLink || !discoverLink) {
        return;
    }

    historyLink.addEventListener("click", (event) => {
        event.preventDefault();

        setActiveNav("history");
        renderHistory();
    });

    discoverLink.addEventListener("click", (event) => {
        event.preventDefault();

        setActiveNav("discover");

        const input =
            document.getElementById("queryInput");

        if (input) {
            input.focus();
        }
    });
}

document.addEventListener(
    "DOMContentLoaded",
    setupSearch
);

document.addEventListener(
    "DOMContentLoaded",
    setupHistory
);