// Helper: scrape a single metric value from a given table
function findMetric(tableId, metricName) {
  const table = document.getElementById(tableId);
  if (!table) {
    console.error(`Table element with ID ${tableId} not found`);
    return 0;
  }
  const rows = table.querySelectorAll('tbody tr');
  for (let row of rows) {
    if (row.cells[0].textContent.trim() === metricName) {
      const value = row.cells[1].textContent.trim();
      return parseFloat(value.replace('%', '')) || 0;
    }
  }
  return 0;
}

// Helper: reads JSON data attributes from a canvas
function readCanvasData(canvasID) {
  const canvasElement = document.getElementById(canvasID);
  if (!canvasElement) {
    console.error(`Canvas element with ID ${canvasID} not found`);
    return { labels: [], wpm: [], accuracy: [] };
  }
  return {
    labels: JSON.parse(canvasElement.dataset.labels || '[]'),
    wpm: JSON.parse(canvasElement.dataset.wpm || '[]'),
    avg_wpm: JSON.parse(canvasElement.dataset.averagewpm || '[]'),
    accuracy: JSON.parse(canvasElement.dataset.accuracy || '[]'),
    avg_acc: JSON.parse(canvasElement.dataset.averageacc || '[]')
  };
}

document.addEventListener('DOMContentLoaded', () => {
  // 1) Render all charts
  const charts = document.querySelectorAll('.statsChart');
  charts.forEach(chart => {
    const data = readCanvasData(chart.id);
    const maxHeight = Math.max(100, ...data.wpm);

    if (data.wpm.length > 1) {
      // Line chart
      new Chart(chart.getContext('2d'), {
        type: 'line',
        data: {
          labels: data.labels,
          datasets: [
            { label: 'Words Per Minute (WPM)', data: data.wpm, borderColor: 'blue', fill: false },
            { label: 'Accuracy', data: data.accuracy, borderColor: 'green', fill: false }
          ]
        },
        options: {
          responsive: true,
          plugins: { legend: { position: 'top' } },
          scales: { y: { beginAtZero: true, max: maxHeight } }
        }
      });
    } else {
      // Bar chart for single-point
      new Chart(chart.getContext('2d'), {
        type: 'bar',
        data: {
          labels: ['Average WPM','Average Accuracy'],
          datasets: [{
            data: [ data.avg_wpm, Number(data.avg_acc) ],
            borderWidth: 2,
            barPercentage: 0.4,
            categoryPercentage: 0.5
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true, max: maxHeight } }
        }
      });
    }
  });

  // 2) Show "Today" by default
  showTable('1');

  // 3) Generate-report handler
  const genBtn = document.getElementById('generateReportBtn');
  if (genBtn) {
    genBtn.addEventListener('click', () => {
      const userId = document.querySelector('.user-id').textContent.replace(/\D/g,'');
      const period = currentPeriod;
      const tableId = `table-${period}`;
      const chartId = `chart-${period}`;

      // gather stats
      const stats = Array.from(document.querySelectorAll(`#${tableId} tbody tr`))
        .map(tr => ({
          metric: tr.cells[0].textContent.trim(),
          value:  tr.cells[1].textContent.trim(),
          timestamp: tr.cells[2].textContent.trim(),
          paragraph: tr.cells[3].textContent.trim()
        }));

      let chartData;
      if (period === '7' || period === '28') {
        chartData = readCanvasData(chartId);
      } else {
        chartData = {
          labels: [],
          wpm: [ findMetric(tableId, 'Average WPM') ],
          accuracy: [ findMetric(tableId, 'Average Accuracy') ]
        };
      }

      const payload = { stats, ...chartData };

      fetch(`/friends_stats/generate_report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          period,
          data: payload
        })
      })
      .then(res => res.ok ? res.json() : Promise.reject(res.statusText))
      .then(data => {
        if (data.url) window.location.href = data.url;
        else alert('No report URL returned.');
      })
      .catch(err => {
        console.error('Report error', err);
        alert('Failed to generate report: ' + err);
      });
    });
  }
});

// keep track of current period
let currentPeriod = '1';

function showTable(period) {
  currentPeriod = period;
  const allVis = [...document.querySelectorAll('.statsTable'),
                  ...document.querySelectorAll('.statsChart')];
  allVis.forEach(el => {
    const id = el.id;
    if (id === `table-${period}`)      el.style.display = 'table';
    else if (id === `chart-${period}`) el.style.display = 'block';
    else                               el.style.display = 'none';
  });

  document.querySelectorAll('[id^=filter-button]').forEach(btn => {
    btn.className = (btn.id === `filter-button-${period}`) ? 'selected' : 'bg-0';
  });
}