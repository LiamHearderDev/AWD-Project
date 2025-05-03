// Only run this once per load (or when coming back via back-forward cache)
function initSharedChart() {
    const canvas = document.getElementById('statsChart');
    if (!canvas) return;
  
    // Helper: scrape a numeric metric from the stats table
    function findMetric(name) {
      for (let row of document.querySelectorAll('#statsTable tbody tr')) {
        if (row.cells[0].textContent.trim() === name) {
          return parseFloat(
            row.cells[1].textContent.trim().replace('%','')
          );
        }
      }
      return null;
    }
  
    const ctx      = canvas.getContext('2d');
    const period   = canvas.dataset.period;      
    const labels   = JSON.parse(canvas.dataset.labels   || '[]');
    const wpm      = JSON.parse(canvas.dataset.wpm      || '[]');
    const accuracy = JSON.parse(canvas.dataset.accuracy || '[]');
  
    // Linear chart for 7-day & 28-day
    if (period === '7' || period === '28') {
      new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [
            { label: 'Average WPM',           data: wpm,      borderColor: 'blue', fill: false },
            { label: 'Average Accuracy (%)',  data: accuracy, borderColor: 'green', fill: false }
          ]
        },
        options: {
          responsive: true,
          plugins: { legend: { position: 'top' } },
          scales: { y: { beginAtZero: true, max: 100 } }
        }
      });
    }
    // Bar chart for Today & All
    else {
      const avgW = findMetric('Average WPM');
      const avgA = findMetric('Average Accuracy');
      const barColors = ['#3CC47C','#1E392A'];
  
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Average WPM','Average Accuracy'],
          datasets: [{
            data: [ avgW || 0, avgA || 0 ],
            backgroundColor: barColors.map(c => c + 'BF'), // 75% opacity
            borderColor: barColors,
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
  }
  
  // Bind on initial load and when restored from bfcache
  window.addEventListener('DOMContentLoaded', initSharedChart);
  window.addEventListener('pageshow', (evt) => {
    if (evt.persisted) initSharedChart();
  });