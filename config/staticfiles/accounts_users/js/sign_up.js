document.addEventListener("DOMContentLoaded", function () {
  const input = document.getElementById("id_judicial_record");
  const preview = document.getElementById("pdf-preview");

  if (input) {
    input.addEventListener("change", function () {
      const file = input.files[0];
      if (file && file.type === "application/pdf") {
        const reader = new FileReader();
        reader.onload = function (e) {
          preview.innerHTML = `<embed src="${e.target.result}" type="application/pdf" width="100%" height="300px" />`;
        };
        reader.readAsDataURL(file);
      } else {
        preview.innerHTML = "<p class='text-danger'>Fichier non pris en charge. Format PDF requis.</p>";
      }
    });
  }
});
