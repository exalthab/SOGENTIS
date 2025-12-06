document.addEventListener("DOMContentLoaded", function () {

    setTimeout(() => {

        const tabButtons = document.querySelectorAll(".tab-btn");
        const tabContents = document.querySelectorAll(".tab-content");

        if (!tabButtons.length || !tabContents.length) return;

        // Activer le premier onglet par défaut
        tabButtons[0].classList.add("active");
        tabContents[0].classList.remove("hidden");
        tabContents[0].classList.add("show");

        tabButtons.forEach(button => {
            button.addEventListener("click", function () {

                const id = this.dataset.id;
                const targetContent = document.getElementById(`tab-${id}`);

                if (!targetContent) return;

                // Désactiver tous les onglets
                tabButtons.forEach(btn => btn.classList.remove("active"));
                tabContents.forEach(content => {
                    content.classList.add("hidden");
                    content.classList.remove("show");
                });

                // Activer l'onglet cliqué
                this.classList.add("active");
                targetContent.classList.remove("hidden");
                targetContent.classList.add("show");

            });
        });

    }, 50); // attendre le rendu Django
});





// document.addEventListener("DOMContentLoaded", function () {
//     // Ajouter un léger délai avant l'exécution du script
//     setTimeout(() => {
//         const accordionHeaders = document.querySelectorAll('.accordion-header');

//         // Ajouter un gestionnaire d'événements à chaque en-tête de l'accordéon
//         accordionHeaders.forEach(header => {
//             header.addEventListener('click', function () {
//                 const contentId = this.dataset.id;
//                 const content = document.querySelector(`#accordion-content-${contentId}`);

//                 // Vérifier si le contenu est actuellement caché ou ouvert
//                 if (content.classList.contains('hidden')) {
//                     openAccordionContent(content, this);  // Ouvrir la section
//                 } else {
//                     closeAccordionContent(content, this); // Fermer la section
//                 }

//                 // Fermer toutes les autres sections
//                 closeOtherSections(content);
//             });
//         });

//         // Fonction pour ouvrir le contenu
//         function openAccordionContent(content, header) {
//             content.classList.remove('hidden');
//             content.classList.add('open');
//             header.setAttribute('aria-expanded', 'true');
//         }

//         // Fonction pour fermer le contenu
//         function closeAccordionContent(content, header) {
//             content.classList.remove('open');
//             content.classList.add('hidden');
//             header.setAttribute('aria-expanded', 'false');
//         }

//         // Fonction pour fermer toutes les autres sections
//         function closeOtherSections(activeContent) {
//             const allContents = document.querySelectorAll('.accordion-content');
//             allContents.forEach(item => {
//                 if (item !== activeContent) {
//                     closeAccordionContent(item, item.previousElementSibling);
//                 }
//             });
//         }
//     }, 50); // Délai de 50ms avant d'exécuter la fonction
// });
