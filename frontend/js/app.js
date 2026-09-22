const queryInput = document.getElementById("queryInput");
const findButton = document.getElementById("findButton");

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

        findButton.innerHTML = `
            <span>Found ${data.results.length} results ✓</span>
        `;

        console.log("Results:", data.results);

        setTimeout(() => {

            findButton.innerHTML = `
                <span>Find out</span>
                <span class="arrow">→</span>
            `;

            findButton.disabled = false;

        }, 2000);

    } catch (error) {

        console.error("KyaPata error:", error);

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