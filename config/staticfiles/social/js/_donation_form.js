// --------------------------------------------------
// MONTANTS RAPIDES
// --------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    const amountButtons = document.querySelectorAll(".amount-btn");
    const amountField = document.getElementById("id_amount");

    amountButtons.forEach(btn => {
        btn.addEventListener("click", () => {

            // Reset active states
            amountButtons.forEach(b => b.classList.remove("active"));

            const val = btn.dataset.amount;

            // If "Autre"
            if (!val) {
                amountField.value = "";
                btn.classList.add("active");
                amountField.focus();
                return;
            }

            // Set selected amount
            amountField.value = val;
            btn.classList.add("active");
        });
    });
});


// --------------------------------------------------
// PREVIEW ENFANT SÉLECTIONNÉ
// --------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {

    const childSelect = document.getElementById("id_child");
    if (!childSelect) return;

    const previewWrapper = document.getElementById("child-preview");
    const previewImg = document.getElementById("child-preview-img");
    const previewName = document.getElementById("child-preview-name");
    const previewID = document.getElementById("child-preview-id");

    const updatePreview = () => {
        const opt = childSelect.selectedOptions[0];
        if (!opt) return;

        const img = opt.dataset.img;
        const name = opt.dataset.name || opt.textContent.trim();
        const id = opt.dataset.id || opt.value;

        if (!img) {
            previewWrapper.style.display = "none";
            return;
        }

        previewImg.src = img;
        previewName.textContent = name;
        previewID.textContent = "ID : " + id;
        previewWrapper.style.display = "flex";
    };

    childSelect.addEventListener("change", updatePreview);

    // Load on page if child already selected
    if (childSelect.value) updatePreview();
});





// /* ============================================================
//    donation_form.js — SOGENTIS v4.4
//    - Sélection rapide de montants
//    - Activation visuelle du bouton sélectionné
//    ============================================================ */

// document.addEventListener("DOMContentLoaded", () => {

//     const amountButtons = document.querySelectorAll(".amount-btn");
//     const amountInput = document.getElementById("id_amount");

//     if (amountButtons.length && amountInput) {
//         amountButtons.forEach(btn => {
//             btn.addEventListener("click", () => {

//                 // Réinitialiser tous les boutons
//                 amountButtons.forEach(b => b.classList.remove("active"));

//                 // Activer le bouton cliqué si un montant est défini
//                 if (btn.dataset.amount !== "") {
//                     btn.classList.add("active");
//                     amountInput.value = btn.dataset.amount;
//                 } else {
//                     // Si "Autre", on clear et focus
//                     amountInput.value = "";
//                     amountInput.focus();
//                 }
//             });
//         });
//     }

// });
