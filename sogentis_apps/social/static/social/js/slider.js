document.addEventListener('DOMContentLoaded', () => {
  const carousels = document.querySelectorAll('.carousel');

  carousels.forEach((carousel) => {
    // Vérifie s'il existe déjà une instance Bootstrap
    if (!bootstrap.Carousel.getInstance(carousel)) {
      new bootstrap.Carousel(carousel, {
        interval: 5000,  // Temps entre chaque slide (ms)
        ride: 'carousel', // Lance automatiquement
        wrap: true,       // Retour à la première slide à la fin
        pause: 'hover',   // Met en pause au survol (optionnel)
        touch: true       // Support tactile (par défaut true)
      });
    }
  });
});
