document.addEventListener("DOMContentLoaded", function () {

    // ---------------------------
    // Boutons montant rapide
    // ---------------------------
    const amountButtons = document.querySelectorAll(".amount-btn");
    const amountInput = document.querySelector("#id_amount");

    amountButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            // Supprime la classe active sur tous
            amountButtons.forEach(b => b.classList.remove("active"));

            // Active le bouton cliqué
            btn.classList.add("active");

            // Met à jour le champ montant
            const value = btn.dataset.amount;
            if (amountInput) {
                amountInput.value = value || "";
                amountInput.focus();
            }
        });
    });

    // ---------------------------
    // Aperçu enfant sélectionné
    // ---------------------------
    const childSelect = document.querySelector("#id_child");
    const childPreview = document.querySelector("#child-preview");
    const childPreviewImg = document.querySelector("#child-preview-img");
    const childPreviewName = document.querySelector("#child-preview-name");
    const childPreviewId = document.querySelector("#child-preview-id");

    if (childSelect && childPreview) {
        childSelect.addEventListener("change", () => {
            const selectedOption = childSelect.selectedOptions[0];
            if (selectedOption && selectedOption.value) {
                childPreview.style.display = "flex";
                childPreviewImg.src = selectedOption.dataset.photo || "";
                childPreviewName.textContent = selectedOption.textContent;
                childPreviewId.textContent = `ID: ${selectedOption.value}`;
            } else {
                childPreview.style.display = "none";
            }
        });
    }

});
