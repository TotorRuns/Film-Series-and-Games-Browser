const express = require('express');
const fetch = require('node-fetch');
const path = require('path');
require('dotenv').config();

const app = express();
const port = 3000;

let currentPage = 1;
let totalResults = 0;

app.use(express.static('public'));
app.use(express.json());

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.post('/searchMovies', async (req, res) => {
    const query = req.body.query;
    const omdbApiKey = process.env.OMDB_API_KEY;
    const tmdbApiKey = process.env.TMDB_API_KEY;

    if (!omdbApiKey || !tmdbApiKey) {
        return res.status(500).json({ error: 'Fehler: API-Schlüssel nicht gefunden' });
    }

    try {
        const omdbResponse = await fetch(`https://www.omdbapi.com/?apikey=${omdbApiKey}&s=${query}&page=${currentPage}`);
        const omdbData = await omdbResponse.json();

        if (omdbData.Response === "False") {
            return res.status(404).json({ error: 'Fehler: Keine Ergebnisse gefunden' });
        }

        totalResults = parseInt(omdbData.totalResults);
        const results = [];

        for (const movie of omdbData.Search) {
            if (movie.Type === "game") {
                const rawgData = await searchRAWGGames(movie.Title);
                if (rawgData.length > 0) {
                    const game = rawgData[0];
                    const posterUrl = game.background_image ? game.background_image : 'https://via.placeholder.com/100';

                    results.push({
                        poster: posterUrl,
                        title: game.name,
                        year: new Date(game.released).getFullYear(),
                        type: 'Spiel'
                    });
                } else {
                    console.error('Fehler: Keine Ergebnisse für das Spiel gefunden');
                }
            } else {
                const tmdbResponse = await fetch(`https://api.themoviedb.org/3/search/movie?api_key=${tmdbApiKey}&query=${encodeURIComponent(movie.Title)}&language=en`);
                const tmdbData = await tmdbResponse.json();
                const exactMatch = tmdbData.results.find(result => result.title && result.title.toLowerCase() === movie.Title.toLowerCase());
                const posterPath = exactMatch ? exactMatch.poster_path : null;
                const posterUrl = posterPath ? `https://image.tmdb.org/t/p/w500${posterPath}` : 'https://via.placeholder.com/100';

                results.push({
                    poster: posterUrl,
                    title: movie.Title,
                    year: movie.Year,
                    type: movie.Type
                });
            }
        }

        res.json({ results, totalResults });
    } catch (error) {
        console.error('Fehler:', error);
        res.status(500).json({ error: 'Interner Serverfehler' });
    }
});

async function searchRAWGGames(title) {
    const rawgApiKey = process.env.RAWG_API_KEY;

    if (!rawgApiKey) {
        console.error('Fehler: API-Schlüssel für RAWG nicht gefunden');
        return [];
    }

    try {
        await new Promise(resolve => setTimeout(resolve, 250)); // Warte 250ms zwischen den Anfragen
        const rawgResponse = await fetch(`https://api.rawg.io/api/games?key=${rawgApiKey}&search=${title}`);

        if (rawgResponse.status === 401) {
            console.error('Fehler: Ungültiger API-Schlüssel für RAWG');
            return [];
        }

        const rawgData = await rawgResponse.json();
        return rawgData.results.filter(game => !game.tags.some(tag => tag.name.toLowerCase() === 'fan game'));
    } catch (error) {
        console.error('Error fetching RAWG games:', error);
        return []; // Return empty array on error
    }
}

app.listen(port, () => {
    console.log(`Server läuft auf http://localhost:${port}`);
});
