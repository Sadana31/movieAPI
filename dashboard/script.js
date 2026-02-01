const BASE_URL = "https://movieapi-8sg7.onrender.com";

async function getRecommendations() {
    const title = document.getElementById('movieInput').value.trim();
    const director = document.getElementById('directorInput').value.trim();
    const genre = document.getElementById('genreInput').value.trim();
    const rating = document.getElementById('ratingInput').value || 6.5;
    const limit = document.getElementById('limitInput')?.value || 12;
    
    const grid = document.getElementById('movieGrid');
    grid.innerHTML = "<h2 style='grid-column: 1/-1; text-align: center;'>✨ Mixing the Magic...</h2>";

    try {
        let response;
        
        // --- LOGIC: IF TITLE IS EMPTY, USE /FILTER ---
        if (!title) {
            // Sends the exact POST body your API expects
            const filterBody = {
                runtime: 0,
                director: director || "", 
                cast: "",                 
                language: "",             
                genre: genre || "",       
                limit: parseInt(limit)
            };

            response = await fetch(`${BASE_URL}/filter`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(filterBody)
            });
        } 
        // --- LOGIC: IF TITLE EXISTS, USE /RECOMMEND ---
        else {
            response = await fetch(`${BASE_URL}/recommend`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: title,
                    top_k: parseInt(limit),
                    min_rating: parseFloat(rating)
                })
            });
        }

        const data = await response.json();
        
        // Handle different key names from different endpoints (recommendations vs results)
        const movies = data.recommendations || data.results || [];
        
        if (movies.length === 0) {
            grid.innerHTML = "<h2 style='grid-column: 1/-1; text-align: center;'>🕵️ No movies found! Try different filters.</h2>";
            return;
        }

        displayMiniCards(movies);

    } catch (err) {
        grid.innerHTML = "<h2 style='grid-column: 1/-1; text-align: center;'>😴 API is warming up or an error occurred.</h2>";
    }
}

function displayMiniCards(movies) {
    const grid = document.getElementById('movieGrid');
    grid.innerHTML = movies.map(m => `
        <div class="movie-card">
            <span class="rating-pill">⭐ ${m.rating || m.vote_average || 'N/A'}</span>
            <h3>${m.title || m.original_title}</h3>
            <span style="font-size: 2rem;">🎬</span>
        </div>
    `).join('');
}

// --- EVENT LISTENERS ---

// Click Search Button
document.getElementById('getRecsBtn').addEventListener('click', getRecommendations);

// Enter Key Listener for ALL Inputs
const allInputs = ['movieInput', 'directorInput', 'genreInput', 'ratingInput', 'limitInput'];
allInputs.forEach(id => {
    const inputElement = document.getElementById(id);
    if (inputElement) {
        inputElement.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                getRecommendations();
            }
        });
    }
});