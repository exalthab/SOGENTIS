document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("live-search-input");
    const resultsBox = document.getElementById("live-search-results");

    let controller = null; // abort previous queries

    input.addEventListener("input", async () => {
        const q = input.value.trim();

        if (!q) {
            resultsBox.innerHTML = "";
            resultsBox.style.display = "none";
            return;
        }

        // Abort previous request
        if (controller) controller.abort();
        controller = new AbortController();

        try {
            const res = await fetch(`/search/ajax/?q=${encodeURIComponent(q)}`, {
                signal: controller.signal
            });

            const data = await res.json();
            const results = data.results;

            if (results.length === 0) {
                resultsBox.innerHTML = `<div class="live-no-result">Aucun résultat</div>`;
                resultsBox.style.display = "block";
                return;
            }

            resultsBox.innerHTML = results
                .map(r => `
                    <a href="${r.url}" class="live-item" target="_blank">
                        <span class="live-title">${r.title}</span>
                        <span class="live-type">${r.type}</span>
                    </a>
                `).join("");

            resultsBox.style.display = "block";

        } catch (err) {
            // ignore aborted fetch
        }
    });

    // Hide results when clicking elsewhere
    document.addEventListener("click", (e) => {
        if (!resultsBox.contains(e.target) && e.target !== input) {
            resultsBox.style.display = "none";
        }
    });
});
