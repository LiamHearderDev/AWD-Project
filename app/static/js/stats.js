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
    avg_wpm: JSON.parse(canvasElement.dataset.averagewpm || '[]'),
    accuracy: JSON.parse(canvasElement.dataset.accuracy || '[]'),
    avg_acc: JSON.parse(canvasElement.dataset.averageacc || '[]')
  };
}


// Initialize all charts once DOM is ready
document.addEventListener('DOMContentLoaded', () => {

  // Loop over every chart element and populate them with data
  const $charts = $(".statsChart");
  for (let i = 0; i < $charts.length; i++){
    const chart = $charts[i];                   // Converts into DOM object
    if (chart == null || chart == undefined) {  // Catch if invalid
      flash("An unexpected error occurred while displaying your statistics. Please try again later.");
      break;
    }

    const canvasData = readCanvasData(chart.id);
    const maxChartHeight = Math.max(100, ...canvasData.wpm);

    // If there is 1 data point, make it a bar chart.
    // If there is >1 data point, make it a line chart.
    if (canvasData.wpm.length > 1){
      // Line graph
      new Chart(chart.getContext('2d'), {
        type: 'line',
        data: {
          labels: canvasData.labels,
          datasets: [
            { label: 'Words Per Minute (WPM)', data: canvasData.wpm, borderColor: 'blue',  fill: false }
            // { label: 'Accuracy',  data: canvasData.accuracy, borderColor: 'green', fill: false }
          ]
        },
        options: {
          responsive: true,
          plugins: { 
            legend: { position: 'top' }
          },
          scales: { y: { beginAtZero: true, max: maxChartHeight } }
        }
      });
    } 
    else {
      // Bar graph
      new Chart(chart.getContext('2d'), {
        type: 'bar',
        data: {
          labels: ['Average WPM'],
          datasets: [
            {
              data: [ canvasData.avg_wpm, Number(canvasData.avg_acc.replace("%", ""))],
              backgroundColor: ['#3CC47CBF','#1E392ABF'],
              borderColor: ['#3CC47C','#1E392A'],
              borderWidth: 2,
              barPercentage: 0.4,
              categoryPercentage: 0.5
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false }
          },
          scales: { y: { beginAtZero: true, max: maxChartHeight } }
        }
      });
    }
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

  showDoughnutChart(period);
  showCorrectDoughnutChart(period);
  const $paraTables = $(".paragraphStatsTable");
  $paraTables.each((_, tbl) => {
    tbl.style.display = tbl.id === "para-table-" + period ? "table" : "none";
  });

  // Select the button that was pressed, deselect all other buttons
  $buttons = $("button[id^='filter-button']");
  $buttons.removeClass("selected");
  $(`#filter-button-${period}`).addClass("selected");
}


let mistakeWordsChartInstance = null;

function showDoughnutChart(period) {
  const canvas = document.getElementById('mistake-words-chart');
  if (!canvas) return;

  const suffixMap = {
    '1': 'today',
    '7': 'last7',
    '28': 'last28',
    'all': 'all'
  };
  const suffix = suffixMap[period];

  const labels = JSON.parse(canvas.dataset[`labels${capitalize(suffix)}`] || "[]");
  const counts = JSON.parse(canvas.dataset[`counts${capitalize(suffix)}`] || "[]");

  if (!labels.length || !counts.length) {
    console.warn("No mistake word data found for period:", period);
    return;
  }

  // clear the canvas before drawing
  if (mistakeWordsChartInstance) {
    mistakeWordsChartInstance.destroy();
  }

  mistakeWordsChartInstance = new Chart(canvas.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        label: "Most Mistyped Words",
        data: counts,
        backgroundColor: labels.map(() => `hsl(${Math.random() * 360}, 70%, 70%)`)
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'top' },
        title: { display: true, text: 'Most Mistyped Words' }
      }
    }
  });
}

let correctWordsChartInstance = null;

function showCorrectDoughnutChart(period) {
  const canvas = document.getElementById('correct-words-chart');
  if (!canvas) return;

  const suffixMap = { '1': 'today', '7': 'last7', '28': 'last28', 'all': 'all' };
  const suffix = suffixMap[period];

  const labels = JSON.parse(canvas.dataset[`labels${capitalize(suffix)}`] || "[]");
  const counts = JSON.parse(canvas.dataset[`counts${capitalize(suffix)}`] || "[]");

  if (!labels.length || !counts.length) return;

  if (correctWordsChartInstance) correctWordsChartInstance.destroy();

  correctWordsChartInstance = new Chart(canvas.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        label: "Most Correct Words",
        data: counts,
        backgroundColor: labels.map(() => `hsl(${Math.random() * 360}, 60%, 70%)`)
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'top' },
        title: { display: true, text: 'Most Correct Words' }
      }
    }
  });
}

function capitalize(str) {
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
      wpm: [findMetric('table-' + currentPeriod, 'Average WPM')]
      // accuracy: [findMetric('table-' + currentPeriod, 'Average Accuracy')] 
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
