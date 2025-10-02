document.addEventListener('DOMContentLoaded', () => {
    const movieList = document.getElementById('movie-list');

    fetch('/api/movies/')
        .then(response => response.json())
        .then(movies => {
            if (movies.length === 0) {
                movieList.innerHTML = '<p>No movies found. Add some via the API!</p>';
                return;
            }
            movies.forEach(movie => {
                const movieDiv = document.createElement('div');
                movieDiv.className = 'movie';
                movieDiv.innerHTML = `
                    <h3>${movie.title}</h3>
                    <p><strong>Director:</strong> ${movie.director}</p>
                    <p><strong>Year:</strong> ${movie.year}</p>
                `;
                movieList.appendChild(movieDiv);
            });
        })
        .catch(error => {
            console.error('Error fetching movies:', error);
            movieList.innerHTML = '<p>Error loading movies. Is the API running?</p>';
        });
});