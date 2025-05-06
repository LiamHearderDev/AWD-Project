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

// Helper: read JSON data attributes from a canvas
function readCanvasData(canvasId) {
  const el = document.getElementById(canvasId);
  if (!el) {
    console.error(`Canvas element with ID ${canvasId} not found`);
    return { labels: [], wpm: [], accuracy: [] };
  }
  
  return {
    labels: JSON.parse(el.dataset.labels || '[]'),
    wpm: JSON.parse(el.dataset.wpm || '[]'),
    accuracy: JSON.parse(el.dataset.accuracy || '[]')
  };
}

// Initialize all charts once DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  // TODAY BAR CHART
  const ctxToday = document.getElementById('chartToday');
  if (ctxToday) {
    const dToday = readCanvasData('chartToday');
    // Use data attributes if available, otherwise fall back to findMetric
    const wpmValue = dToday.wpm.length > 0 ? dToday.wpm[0] : findMetric('tableToday', 'Average WPM');
    const accValue = dToday.accuracy.length > 0 ? dToday.accuracy[0] : findMetric('tableToday', 'Average Accuracy');
    
    new Chart(ctxToday.getContext('2d'), {
      type: 'bar',
      data: {
        labels: ['Average WPM','Average Accuracy'],
        datasets: [{
          data: [wpmValue, accValue],
          backgroundColor: ['#3CC47CBF','#1E392ABF'],
          borderColor: ['#3CC47C','#1E392A'],
          borderWidth: 2,
          barPercentage: 0.4,
          categoryPercentage: 0.5
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, max: 100 } }
      }
    });
  }

  // LAST 7 DAYS LINE CHART
  const c7 = document.getElementById('chart7');
  if (c7) {
    const d7 = readCanvasData('chart7');
    new Chart(c7.getContext('2d'), {
      type: 'line',
      data: {
        labels: d7.labels,
        datasets: [
          { label: 'Average WPM',           data: d7.wpm,      borderColor: 'blue',  fill: false },
          { label: 'Average Accuracy (%)',  data: d7.accuracy, borderColor: 'green', fill: false }
        ]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'top' } },
        scales: { y: { beginAtZero: true, max: 100 } }
      }
    });
  }

  // LAST 28 DAYS LINE CHART
  const c28 = document.getElementById('chart28');
  if (c28) {
    const d28 = readCanvasData('chart28');
    new Chart(c28.getContext('2d'), {
      type: 'line',
      data: {
        labels: d28.labels,
        datasets: [
          { label: 'Average WPM',           data: d28.wpm,      borderColor: 'blue',  fill: false },
          { label: 'Average Accuracy (%)',  data: d28.accuracy, borderColor: 'green', fill: false }
        ]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'top' } },
        scales: { y: { beginAtZero: true, max: 100 } }
      }
    });
  }

  // ALL-TIME BAR CHART
  const ctxAll = document.getElementById('chartAll');
  if (ctxAll) {
    const dAll = readCanvasData('chartAll');
    // Use data attributes if available, otherwise fall back to findMetric
    const wpmValue = dAll.wpm.length > 0 ? dAll.wpm[0] : findMetric('tableAll', 'Average WPM');
    const accValue = dAll.accuracy.length > 0 ? dAll.accuracy[0] : findMetric('tableAll', 'Average Accuracy');
    
    new Chart(ctxAll.getContext('2d'), {
      type: 'bar',
      data: {
        labels: ['Average WPM','Average Accuracy'],
        datasets: [{
          data: [wpmValue, accValue],
          backgroundColor: ['#3CC47CBF','#1E392ABF'],
          borderColor: ['#3CC47C','#1E392A'],
          borderWidth: 2,
          barPercentage: 0.4,
          categoryPercentage: 0.5
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, max: 100 } }
      }
    });
  }

  // Show 'today' by default
  showTable('today');
  
  // Debug logging to help troubleshoot
  console.log('Today data:', readCanvasData('chartToday'));
  console.log('7-day data:', readCanvasData('chart7'));
  console.log('28-day data:', readCanvasData('chart28'));
  console.log('All-time data:', readCanvasData('chartAll'));
});

// Keep track of which period is active
let currentPeriod = 'today';

// Show/hide tables and canvases
function showTable(period) {
  currentPeriod = period;
  ['tableToday','table7','table28','tableAll'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
  });
  ['chartToday','chart7','chart28','chartAll'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
  });
  
  const table = document.getElementById('table' + capitalize(period));
  if (table) table.style.display = 'table';
  
  const chart = document.getElementById('chart' + capitalize(period));
  if (chart) chart.style.display = 'block';
}

// Utility to capitalize 'today', '7', '28', 'All'
function capitalize(str) {
  if (str === '7' || str === '28') return str;
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// Attach generate-report handler
const genBtn = document.getElementById('generateReportBtn');
if (genBtn) genBtn.addEventListener('click', () => {
  const userIdElement = document.querySelector('.user-id');
  if (!userIdElement) {
    console.error('User ID element not found');
    alert('Could not find user ID');
    return;
  }
  
  const userIdMatch = userIdElement.textContent.match(/ID: (\d+)/);
  if (!userIdMatch) {
    console.error('Could not extract user ID from element');
    alert('Could not extract user ID');
    return;
  }
  
  const userId = userIdMatch[1];
  const tableId = 'table' + capitalize(currentPeriod);
  const chartId = 'chart' + currentPeriod;
  
  const stats = Array.from(document.querySelectorAll(`#${tableId} tbody tr`))
    .map(tr => ({ 
      metric: tr.cells[0].textContent.trim(), 
      value: tr.cells[1].textContent.trim(),
      timestamp: tr.cells[2].textContent.trim(), 
      paragraph: tr.cells[3].textContent.trim() 
    }));
  
  let chartData;
  if (currentPeriod === '7' || currentPeriod === '28') {
    chartData = readCanvasData(chartId);
  } else {
    chartData = { 
      labels: [], 
      wpm: [findMetric('table' + capitalize(currentPeriod), 'Average WPM')],
      accuracy: [findMetric('table' + capitalize(currentPeriod), 'Average Accuracy')] 
    };
  }
  
  const payload = { stats, ...chartData };
  
  fetch('/stats/generate_report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `userid=${userId}&period=${currentPeriod}&data=${encodeURIComponent(JSON.stringify(payload))}`
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    if (data.url) {
      window.location.href = data.url;
    } else {
      alert('No URL returned in the response');
    }
  })
  .catch(error => {
    console.error('Error generating report:', error);
    alert('Failed to generate report: ' + error.message);
  });
});
