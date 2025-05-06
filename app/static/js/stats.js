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

  // Get the canvas HTML element
  const canvasElement = document.getElementById(canvasID);

  // If the canvas we're reading doesn't exist, flash an error and return.
  if (canvasElement == null || canvasElement == undefined) {
    flash("Canvas element with ID ${" + canvasID + "} not found");
    return { labels: [], wpm: [], accuracy: [] };
  }
  
  // Extract and return the data
  return {
    labels: JSON.parse(canvasElement.dataset.labels || '[]'),
    wpm: JSON.parse(canvasElement.dataset.wpm || '[]'),
    accuracy: JSON.parse(canvasElement.dataset.accuracy || '[]')
  };
}

// Initialize all charts once DOM is ready
document.addEventListener('DOMContentLoaded', () => {

  const maxChartHeight = 150;
  // TODAY BAR CHART

  // get chart elements
  // Loop over
    // read canvas data
    // create a new chart with the chart element as the context

  const $charts = $(".statsChart");
  for (let i = 0; i < $charts.length; i++){
    const chart = $charts[i];                   // Converts into DOM object
    if (chart == null || chart == undefined) {  // Catch if invalid
      flash("An unexpected error occurred while displaying your statistics. Please try again later.");
      break;
    }

    const canvasData = readCanvasData(chart.id);

    new Chart(chart.getContext('2d'), {
      type: 'line',
      data: {
        labels: canvasData.labels,
        datasets: [
          { label: 'Average WPM',           data: canvasData.wpm,      borderColor: 'blue',  fill: false },
          { label: 'Average Accuracy (%)',  data: canvasData.accuracy, borderColor: 'green', fill: false }
        ]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'top' } },
        scales: { y: { beginAtZero: true, max: maxChartHeight } }
      }
    });
  }

  // Show 'today' by default
  showTable('1');
  
  // Debug logging to help troubleshoot
  console.log("Today's data:", readCanvasData('chart-1'));
  console.log('7-day data:', readCanvasData('chart-7'));
  console.log('28-day data:', readCanvasData('chart-28'));
  console.log('All-time data:', readCanvasData('chart-all'));
});

// Keep track of which period is active
let currentPeriod = '1';

// Show/hide tables and canvases
function showTable(period) {
  if (typeof(period) !== 'string'){
    flash("An error occurred when displaying data. Please try again later.")
    // TODO: Here, hide all tables and charts, and display an error icon.
    return;
  }
  currentPeriod = period;

  // The below code will hide the tables/charts we don't want to see, then show the table/chart we DO want to see.

  const $statTables = $(".statsTable");               // Get all tables with the class "statsTable".
  const $statCharts = $(".statsChart");               // Get all charts with the class "statsChart". 
  const $statVisuals = $statTables.add($statCharts);  // Combine the two jQuery results. 

  for (let i = 0; i < $statVisuals.length; i++) {     // Show the table/chart we want, hide the tables we don't want.
    const element = $statVisuals[i];                  // Getting an array element converts it into a DOM object.
    if (element.id === "table-" + period || element.id === "chart-" + period) { 
      element.style.display = element.id === "chart-" + period ? "block" : "table"; // Set display to "table" if it's a table, otherwise set to block.
    } else {
      element.style.display = "none"; 
    }
  }

  // Now we make the filter-buttons a different colour so we know which one we have clicked.
  const $filterButtons = $("[id^=filter-button]");
  for (let i = 0; i < $filterButtons.length; i++) {
    
  }

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
  const tableId = 'table-' + currentPeriod;
  const chartId = 'chart-' + currentPeriod;
  
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
      wpm: [findMetric('table-' + currentPeriod, 'Average WPM')],
      accuracy: [findMetric('table-' + currentPeriod, 'Average Accuracy')] 
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
