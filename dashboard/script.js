const BASE_URL = "https://movieapi-8sg7.onrender.com";
const movieInput = document.getElementById('movieInput');
const suggestionsBox = document.getElementById('suggestions');
const movieGrid = document.getElementById('movieGrid');
const getRecsBtn = document.getElementById('getRecsBtn');

// Helper to show status to the user
function setStatus(msg) {
    movieGrid.innerHTML = `<p style="text-align:center; color:#e50914; font-weight:bold;">${msg}</p>`;
}

// 1. Live Search (Fuzzy)
movieInput.addEventListener('input', async (e) => {
    const query = e.target.value.trim();
    if (query.length < 2) {
        suggestionsBox.innerHTML = '';
        return;
    }

    try {
        const res = await fetch(`${BASE_URL}/search?query=${encodeURIComponent(query)}&limit=5`);
        if (!res.ok) throw new Error("Server waking up...");
        const data = await res.json();
        
        suggestionsBox.innerHTML = data.results.map(movie => `
            <div class="suggestion-item" onclick="selectMovie('${movie.title.replace(/'/g, "\\'")}')">
                ${movie.title}
            </div>
        `).join('');
    } catch (err) { 
        console.log("Search silent error (server likely sleeping)");
    }
});

function selectMovie(title) {
    movieInput.value = title;
    suggestionsBox.innerHTML = '';
}

// 2. Fetch Recommendations
getRecsBtn.addEventListener('click', async () => {
    const title = movieInput.value.trim();
    if (!title) return alert("Type a movie name first!");

    setStatus("🚀 Waking up the server (this can take 30-50s on Render Free)...");

    try {
        const response = await fetch(`${BASE_URL}/recommend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: title,
                top_k: 10
            })
        });

        if (!response.ok) throw new Error("API Error");

        const data = await response.json();
        displayMovies(data.recommendations);
    } catch (err) {
        setStatus("❌ Failed to connect. Please wait 1 minute for the server to wake up and try again.");
        console.error(err);
    }
});


function displayMovies(movies) {
    console.log("Data received from API:", movies); // CHECK YOUR CONSOLE (F12)

    const grid = document.getElementById('movieGrid');
    
    if (!movies || movies.length === 0) {
        grid.innerHTML = "<p>No movies found in the database.</p>";
        return;
    }

    // Clear the "Loading" text
    grid.innerHTML = "";

    movies.forEach(movie => {
        const card = document.createElement('div');
        card.className = 'movie-card';
        card.innerHTML = `
            <h3>${movie.title}</h3>
            <p>⭐ Rating: ${movie.rating || 'N/A'}</p>
            <p>🎯 Match: ${movie.similarity ? Math.round(movie.similarity * 100) : '??'}%</p>
        `;
        grid.appendChild(card);
    });
}