document.addEventListener("DOMContentLoaded", function () {
    const elements = document.querySelectorAll(".star-rating-detailed");

    elements.forEach(function (ratingElement) {
        let ratingAttr = ratingElement.getAttribute("data-rating") || "0";
        ratingAttr = ratingAttr.replace(",", ".");

        const rating = parseFloat(ratingAttr);

        if (isNaN(rating)) return;

        const starsCount = rating / 2;
        const stars = ratingElement.querySelectorAll(".star");

        stars.forEach((star, index) => {
            star.classList.remove("filled", "half");

            if (starsCount >= index + 1) {
                star.classList.add("filled");
            } else if (starsCount > index && starsCount < index + 1) {
                star.classList.add("half");
            }
        });
    });
});
