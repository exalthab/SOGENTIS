// Vérifie si Chart.js est bien chargé
if (typeof Chart !== "undefined") {
  // 🎯 Inscriptions mensuelles (exemple avec 12 mois)
  const usersChartCtx = document.getElementById("usersChart");
  if (usersChartCtx) {
    new Chart(usersChartCtx, {
      type: "line",
      data: {
        labels: [
          "Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
          "Juil", "Août", "Sept", "Oct", "Nov", "Déc"
        ],
        datasets: [{
          label: "Inscriptions",
          data: [5, 9, 12, 8, 15, 18, 22, 25, 17, 20, 13, 10],
          backgroundColor: "rgba(54, 162, 235, 0.2)",
          borderColor: "rgba(54, 162, 235, 1)",
          borderWidth: 2,
          tension: 0.4,
          fill: true,
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            ticks: { stepSize: 5 }
          }
        }
      }
    });
  }

  // 🎯 Répartition des rôles (exemple statique)
  const rolesChartCtx = document.getElementById("rolesChart");
  if (rolesChartCtx) {
    new Chart(rolesChartCtx, {
      type: "doughnut",
      data: {
        labels: ["Bénévoles", "Membres", "Amis", "Autres"],
        datasets: [{
          label: "Répartition",
          data: [45, 30, 15, 10],
          backgroundColor: [
            "#4e73df", "#1cc88a", "#f6c23e", "#e74a3b"
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    });
  }
} else {
  console.warn("Chart.js non chargé");
}
