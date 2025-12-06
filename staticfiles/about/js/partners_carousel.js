document.addEventListener("DOMContentLoaded", () => {
    new Swiper(".partners-swiper", {
        loop: true,
        slidesPerView: 1,
        spaceBetween: 25,

        autoplay: {
            delay: 2500,
            disableOnInteraction: false,
        },

        pagination: {
            el: ".swiper-pagination",
            clickable: true,
        },

        navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
        },

        breakpoints: {
            640: { slidesPerView: 2 },
            992: { slidesPerView: 3 },
            1200: { slidesPerView: 4 },
        }
    });
});
