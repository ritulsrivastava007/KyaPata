const queryInput = document.getElementById("queryInput");
const findButton = document.getElementById("findButton");

function getResultsContainer() {
    let container = document.getElementById("resultsContainer");

    if (!container) {
        container = document.createElement("section");
        container.id = "resultsContainer";
        container.className = "results-section";

        findButton.closest("main").appendChild(container);
    }

    return container;
}

function formatDate(dateString) {
    if (!dateString) {
        return "Date unavailable";
    }

    const date = new Date(dateString);

    if (Number.isNaN(date.getTime())) {
        return dateString;
    }

    return date.toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric"
    });
}

function renderResults(results, query) {
    const container = getResultsContainer();

    if (!results || results.length === 0) {
        container.innerHTML = `
            <div class="results-header">
                <div>
                    <p class="eyebrow">Search results</p>
                    <h2>No matching results found</h2>
                    <p>Try changing your search or using broader keywords.</p>
                </div>
            </div>
        `;
        return;
    }

    const cards = results.map((job) => `
        <article class="job-card">

            <div class="job-card-top">
                <div>
                    <span class="source-badge">${job.source || "External source"}</span>
                    <h3>${job.title || "Untitled role"}</h3>
                    <p class="company">${job.company || "Company not specified"}</p>
                </div>
            </div>

            <div class="job-meta">

                ${job.location ? `
                    <span>📍 ${job.location}</span>
                ` : ""}

                ${job.level ? `
                    <span>◉ ${job.level}</span>
                ` : ""}

                ${job.published ? `
                    <span>🕒 ${formatDate(job.published)}</span>
                ` : ""}

            </div>

            ${job.description ? `
                <p class="job-description">
                    ${job.description}
                </p>
            ` : ""}

            <div class="job-card-bottom">
                <span class="source-text">
                    Source: ${job.source || "Unknown"}
                </span>

                <a
                    href="${job.url}"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="source-link"
                >
                    View source →
                </a>
            </div>

        </article>
    `).join("");

    container.innerHTML = `
        <div class="results-header">

            <div>
                <p class="eyebrow">Search results</p>
                <h2>${results.length} opportunities found</h2>
                <p>Results for <strong>"${query}"</strong></p>
            </div>

            <div class="results-status">
                Live data ✓
            </div>

        </div>

        <div class="results-list">
            ${cards}
        </div>
    `;

    container.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


findButton.addEventListener("click", async () => {

    const query = queryInput.value.trim();

    if (!query) {
        queryInput.focus();
        return;
    }

    findButton.disabled = true;

    findButton.innerHTML = `
        <span>Finding...</span>
    `;

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/api/query",
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
            throw new Error("Request failed");
        }

        const data = await response.json();

        console.log("KyaPata response:", data);

        renderResults(data.results, query);

        findButton.innerHTML = `
            <span>Found ${data.results.length} results ✓</span>
        `;

        setTimeout(() => {

            findButton.innerHTML = `
                <span>Find out</span>
                <span class="arrow">→</span>
            `;

            findButton.disabled = false;

        }, 1500);

    } catch (error) {

        console.error("KyaPata error:", error);

        const container = getResultsContainer();

        container.innerHTML = `
            <div class="results-error">
                <p class="eyebrow">Something went wrong</p>
                <h2>We couldn't complete the search.</h2>
                <p>
                    Make sure the KyaPata backend is running and try again.
                </p>
            </div>
        `;

        findButton.innerHTML = `
            <span>Something went wrong</span>
        `;

        setTimeout(() => {

            findButton.innerHTML = `
                <span>Find out</span>
                <span class="arrow">→</span>
            `;

            findButton.disabled = false;

        }, 2000);
    }
});