document.querySelector('#recommendationForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const form = event.target;
    const titleInput = document.getElementById('title');
    const recommendationsDiv = document.getElementById('recommendations');

    fetch('/recommend', {
        method: 'POST',
        body: new FormData(form)
    })
    .then(response => response.json())
    .then(data => {
        recommendationsDiv.innerHTML = '';

        if (data.length === 0 || data[0].original_title === "Movie not found") {
            recommendationsDiv.innerHTML = '<p class="error">Sorry, no recommendations found. Please try another movie.</p>';
        } else {
            data.forEach(movie => {
                recommendationsDiv.innerHTML += `
                    <div class="movie">
                        <h3>${movie.original_title}</h3>
                        <p>${movie.overview}</p>
                    </div>
                `;
            });
        }

        titleInput.value = ''; // Clear the input field
    })
    .catch(error => {
        console.error('Error:', error);
        recommendationsDiv.innerHTML = '<p class="error">An error occurred while fetching recommendations. Please try again later.</p>';
    });
});
