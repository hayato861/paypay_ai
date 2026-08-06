const ctx = document.getElementById("scoreChart");

if (ctx) {

    new Chart(ctx, {

        type: "line",

        data: {

            labels: scoreLabels,

            datasets: [{

                label: "市場スコア",

                data: scoreData,

                borderColor: "#38bdf8",

                backgroundColor: "rgba(56,189,248,0.2)",

                fill: true,

                tension: 0.35,

                borderWidth: 3,

                pointRadius: 4

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    display: false

                }

            },

            scales: {

                y: {

                    min: 0,

                    max: 100

                }

            }

        }

    });

}