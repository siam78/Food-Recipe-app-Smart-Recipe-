document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.toggle-favorite');

    buttons.forEach(button => {
        button.addEventListener('click', function() {
            const recipeId = this.getAttribute('data-recipe-id');
            const isFavorite = this.textContent.trim() === 'Remove from Favorites';

            fetch(`/toggle-favorite/${recipeId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.textContent = isFavorite ? 'Add to Favorites' : 'Remove from Favorites';
                    this.classList.toggle('btn-outline-danger');
                    this.classList.toggle('btn-success');
                } else {
                    alert('Error toggling favorite status: ' + data.message);
                }
            })
            .catch(error => {
                alert('Error toggling favorite status: ' + error.message);
            });
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});