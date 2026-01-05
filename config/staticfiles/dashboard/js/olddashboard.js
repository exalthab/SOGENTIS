document.addEventListener("DOMContentLoaded", function() {
  // Graphique principal
  var ctx = document.getElementById("networkChart").getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
      datasets: [{
        label: 'Activité',
        data: [150, 200, 170, 240, 180, 220, 260],
        backgroundColor: 'rgba(24,188,156,0.14)',
        borderColor: '#18bc9c',
        pointBackgroundColor: '#fff',
        borderWidth: 3,
        fill: true,
        tension: .35
      }]
    },
    options: {
      plugins: { legend: { display: false } },
      responsive: true,
      scales: {
        y: { beginAtZero: true }
      }
    }
  });

  // Pie Chart
  var dtx = document.getElementById("deviceUsageChart").getContext('2d');
  new Chart(dtx, {
    type: 'doughnut',
    data: {
      labels: ['iOS', 'Android', 'Web', 'Autres'],
      datasets: [{
        data: [45, 32, 16, 7],
        backgroundColor: ['#18bc9c', '#36a2eb', '#f39c12', '#7d8da1']
      }]
    },
    options: {
      plugins: { legend: { position: 'bottom' } },
      cutout: '65%'
    }
  });
});
