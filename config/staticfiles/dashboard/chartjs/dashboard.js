document.addEventListener("DOMContentLoaded", function() {
    // Graph principal (network)
    var ctx = document.getElementById("networkChart").getContext('2d');
    var networkChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ["Jan 02", "Jan 03", "Jan 04", "Jan 05", "Jan 06"],
            datasets: [{
                label: 'Network Activities',
                data: [120, 170, 110, 250, 160],
                backgroundColor: 'rgba(24, 188, 156, 0.2)',
                borderColor: '#18bc9c',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } }
        }
    });

    // Autres graphiques à l’identique (appVersionsChart, deviceUsageChart, etc)
});
