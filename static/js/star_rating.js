document.addEventListener('DOMContentLoaded', function() {
    function updateStarRating(ratingElement) {
        const ratingAttr = ratingElement.getAttribute('data-rating') || '0';
        const rating = parseFloat(ratingAttr.replace(',', '.')) || 0;
        const stars = ratingElement.querySelectorAll('.star');
        const starsCount = rating / 2;

        stars.forEach((star, index) => {
            star.classList.remove('filled', 'half');

            if (starsCount >= index + 1) {
                star.classList.add('filled');
            } else if (starsCount > index && starsCount < index + 1) {
                star.classList.add('half');
            }
        });
    }

    document.querySelectorAll('.star-rating-detailed[data-rating]').forEach(updateStarRating);
});
