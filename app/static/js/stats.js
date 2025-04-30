const today_stats = [
    {"metric": "Total Attempts", "value": 1, "time": "10:15 a.m. 04/25/2025", "paragraph": 2},
    {"metric": "Best WPM", "value": 75.3, "time": "10:15 a.m. 04/25/2025", "paragraph": 2},
    {"metric": "Best Accuracy", "value": "95.2%", "time": "10:15 a.m. 04/25/2025", "paragraph": 2},
    {"metric": "Best Word Count", "value": 310, "time": "10:15 a.m. 04/25/2025", "paragraph": 2},
    {"metric": "Best Correct Words Count", "value": 295, "time": "10:15 a.m. 04/25/2025", "paragraph": 2},
    {"metric": "Least Mistakes in Words", "value": 5, "time": "10:15 a.m. 04/25/2025", "paragraph": 2}
];

const last7days_stats = [
    {"metric": "Total Attempts", "value": 5, "time": "-", "paragraph": "-"},
    {"metric": "Best WPM", "value": 78.5, "time": "23:14 p.m. 04/15/2025", "paragraph": 3},
    {"metric": "Best Accuracy", "value": "96.4%", "time": "23:14 p.m. 04/15/2025", "paragraph": 3},
    {"metric": "Best Word Count", "value": 325, "time": "23:14 p.m. 04/15/2025", "paragraph": 3},
    {"metric": "Best Correct Words Count", "value": 312, "time": "23:14 p.m. 04/15/2025", "paragraph": 3},
    {"metric": "Least Mistakes in Words", "value": 3, "time": "23:14 p.m. 04/15/2025", "paragraph": 3}
];

const last28days_stats = [
    {"metric": "Total Attempts", "value": 12, "time": "-", "paragraph": "-"},
    {"metric": "Best WPM", "value": 84.2, "time": "19:02 p.m. 04/05/2025", "paragraph": 4},
    {"metric": "Best Accuracy", "value": "97.1%", "time": "19:02 p.m. 04/05/2025", "paragraph": 4},
    {"metric": "Best Word Count", "value": 355, "time": "19:02 p.m. 04/05/2025", "paragraph": 4},
    {"metric": "Best Correct Words Count", "value": 345, "time": "19:02 p.m. 04/05/2025", "paragraph": 4},
    {"metric": "Least Mistakes in Words", "value": 2, "time": "19:02 p.m. 04/05/2025", "paragraph": 4}
];

const alltime_stats = [
    {"metric": "Total Attempts", "value": 37, "time": "-", "paragraph": "-"},
    {"metric": "Best WPM", "value": 88.9, "time": "15:45 p.m. 03/10/2025", "paragraph": 2},
    {"metric": "Best Accuracy", "value": "98.5%", "time": "15:45 p.m. 03/10/2025", "paragraph": 2},
    {"metric": "Best Word Count", "value": 382, "time": "15:45 p.m. 03/10/2025", "paragraph": 2},
    {"metric": "Best Correct Words Count", "value": 377, "time": "15:45 p.m. 03/10/2025", "paragraph": 2},
    {"metric": "Least Mistakes in Words", "value": 1, "time": "15:45 p.m. 03/10/2025", "paragraph": 2}
];

function showTable(period) {
    document.getElementById('tableToday').style.display = 'none';
    document.getElementById('table7').style.display = 'none';
    document.getElementById('table28').style.display = 'none';
    document.getElementById('tableAll').style.display = 'none';

    document.getElementById('chartToday').style.display = 'none';
    document.getElementById('chart7').style.display = 'none';
    document.getElementById('chart28').style.display = 'none';
    document.getElementById('chartAll').style.display = 'none';

    if (period === 'today') {
        document.getElementById('tableToday').style.display = 'table';
        document.getElementById('chartToday').style.display = 'block';
    } else if (period === '7') {
        document.getElementById('table7').style.display = 'table';
        document.getElementById('chart7').style.display = 'block';
    } else if (period === '28') {
        document.getElementById('table28').style.display = 'table';
        document.getElementById('chart28').style.display = 'block';
    } else {
        document.getElementById('tableAll').style.display = 'table';
        document.getElementById('chartAll').style.display = 'block';
    }
}

// Example Data for charts
const todayLabels = ['Attempt 1'];
const todayWPM = [75.3];
const todayAccuracy = [95.2];

const last7daysLabels = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5'];
const last7daysWPM = [72, 74, 78, 76, 79];
const last7daysAccuracy = [94, 95, 96, 95, 97];

const last28daysLabels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
const last28daysWPM = [68, 70, 75, 80];
const last28daysAccuracy = [92, 93, 95, 96];

const alltimeLabels = ['March', 'April'];
const alltimeWPM = [70, 85];
const alltimeAccuracy = [93, 96];

function createLineChart(ctxId, labels, wpmData, accuracyData) {
    const ctx = document.getElementById(ctxId).getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Average WPM',
                    data: wpmData,
                    borderColor: 'blue',
                    fill: false
                },
                {
                    label: 'Average Accuracy (%)',
                    data: accuracyData,
                    borderColor: 'green',
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

window.onload = function() {
    createLineChart('chartToday', todayLabels, todayWPM, todayAccuracy);
    createLineChart('chart7', last7daysLabels, last7daysWPM, last7daysAccuracy);
    createLineChart('chart28', last28daysLabels, last28daysWPM, last28daysAccuracy);
    createLineChart('chartAll', alltimeLabels, alltimeWPM, alltimeAccuracy);
}

document.getElementById("generateReportBtn").addEventListener("click", function(e) {
    e.preventDefault();
    const userid = document.querySelector('.user-id').textContent.split(": ")[1];
    const period = ['today', 'last7days', 'last28days', 'alltime'].find(p => {
        let tableId = '';
        if (p === 'today') tableId = 'tableToday';
        else if (p === 'last7days') tableId = 'table7';
        else if (p === 'last28days') tableId = 'table28';
        else if (p === 'alltime') tableId = 'tableAll';
    
        return document.getElementById(tableId).style.display !== 'none';
    });
    
    const dataMap = {
        today: today_stats,
        last7days: last7days_stats,
        last28days: last28days_stats,
        alltime: alltime_stats
    };
    

    fetch("/stats/generate_report", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `userid=${encodeURIComponent(userid)}&period=${encodeURIComponent(period)}&data=${encodeURIComponent(JSON.stringify({
            stats: dataMap[period],
            labels: period === 'today' ? todayLabels :
                    period === 'last7days' ? last7daysLabels :
                    period === 'last28days' ? last28daysLabels :
                    alltimeLabels,
            wpm: period === 'today' ? todayWPM :
                 period === 'last7days' ? last7daysWPM :
                 period === 'last28days' ? last28daysWPM :
                 alltimeWPM,
            accuracy: period === 'today' ? todayAccuracy :
                      period === 'last7days' ? last7daysAccuracy :
                      period === 'last28days' ? last28daysAccuracy :
                      alltimeAccuracy
        }))}`
    })
    .then(response => response.json())
    .then(data => {
        // redirect or alert
        alert("Shareable URL generated: " + window.location.origin + data.url);
        window.location.href = data.url; 
    })
    .catch(err => {
        console.error("Error generating report:", err);
        alert("Failed to generate report!");
    });
    
});
