// Keep track of which period is active
let currentPeriod = 'today';

function showTable(period) {
  currentPeriod = period;
  // hide all tables & charts
  ['tableToday','table7','table28','tableAll'].forEach(id =>
    document.getElementById(id).style.display = 'none'
  );
  ['chartToday','chart7','chart28','chartAll'].forEach(id =>
    document.getElementById(id).style.display = 'none'
  );

  // show selected table & chart
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

// Create Linear Chart
function createLineChart(ctxId, labels, wpmData, accuracyData) {
  const ctx = document.getElementById(ctxId).getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        { label: 'Average WPM', data: wpmData, borderColor: 'blue', fill: false },
        { label: 'Average Accuracy (%)', data: accuracyData, borderColor: 'green', fill: false }
      ]
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'top' } },
      scales: { y: { beginAtZero: true, max: 100 } }
    }
  });
}

// Create Bar Chart
function createBarChart(ctxId, labels, data) {
  const ctx = document.getElementById(ctxId).getContext('2d');
  const barColors = ['#3CC47C', '#1E392A'];
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: barColors.map(c => c + 'BF'), // 75% opacity fill
        borderColor: barColors,
        borderWidth: 2,
        barPercentage: 0.4,
        categoryPercentage: 0.5
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { autoSkip: false } },
        y: { beginAtZero: true, max: 100 }
      }
    }
  });
}

// SCRAPE A METRIC FROM A TABLE
function findMetric(tableId, metricName) {
  for (let row of document.querySelectorAll(`#${tableId} tbody tr`)) {
    if (row.cells[0].textContent.trim() === metricName) {
      return parseFloat(row.cells[1].textContent.trim().replace('%', ''));
    }
  }
  return null;
}

// READ DATA FROM A CANVAS'S data-* ATTRIBUTES
function readCanvasData(canvasId) {
  const el = document.getElementById(canvasId);
  return {
    labels: JSON.parse(el.dataset.labels || '[]'),
    wpm: JSON.parse(el.dataset.wpm || '[]'),
    accuracy: JSON.parse(el.dataset.accuracy || '[]')
  };
}

// Scrape table 
function scrapeStats(tableId) {
  return Array.from(
    document.querySelectorAll(`#${tableId} tbody tr`)
  ).map(row => ({
    metric: row.cells[0].textContent.trim(),
    value: row.cells[1].textContent.trim(),
    timestamp: row.cells[2].textContent.trim(),
    paragraph: row.cells[3].textContent.trim()
  }));
}

// ON LOAD
window.addEventListener('DOMContentLoaded', function() {
  // show today by default
  showTable('today');

  // draw today's bar chart
  const tW = findMetric('tableToday', 'Average WPM');
  const tA = findMetric('tableToday', 'Average Accuracy');
  if (tW != null && tA != null) createBarChart('chartToday', ['Average WPM', 'Average Accuracy'], [tW, tA]);

  // draw last-7 days line chart
  const d7 = readCanvasData('chart7');
  createLineChart('chart7', d7.labels, d7.wpm, d7.accuracy);

  // draw last-28 days line chart
  const d28 = readCanvasData('chart28');
  createLineChart('chart28', d28.labels, d28.wpm, d28.accuracy);

  // draw all-time bar chart
  const aW = findMetric('tableAll', 'Average WPM');
  const aA = findMetric('tableAll', 'Average Accuracy');
  if (aW != null && aA != null) createBarChart('chartAll', ['Average WPM', 'Average Accuracy'], [aW, aA]);

  // set up generate report button
  const btn = document.getElementById('generateReportBtn');
  if (!btn) return;
  btn.addEventListener('click', function(e) {
    e.preventDefault();
    // grab userId from DOM
    const userId = document.querySelector('.user-id').textContent.split(': ')[1];
    const period = currentPeriod;
    // collect stats and chart data
    const stats = scrapeStats(
      period === 'today' ? 'tableToday' :
      period === '7' ? 'table7' :
      period === '28' ? 'table28' :
      'tableAll'
    );
    const chartData = readCanvasData(
      period === 'today' ? 'chartToday' :
      period === '7' ? 'chart7' :
      period === '28' ? 'chart28' :
      'chartAll'
    );
    // build payload
    const payload = { stats, labels: chartData.labels, wpm: chartData.wpm, accuracy: chartData.accuracy };
    // send it
    fetch('/stats/generate_report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `userid=${encodeURIComponent(userId)}&period=${encodeURIComponent(period)}&data=${encodeURIComponent(JSON.stringify(payload))}`
    })
      .then(r => r.json())
      .then(j => {
        alert('Shareable URL: ' + window.location.origin + j.url);
        window.location.href = j.url;
      })
      .catch(err => {
        console.error(err);
        alert('Failed to generate report!');
      });
  });
});
