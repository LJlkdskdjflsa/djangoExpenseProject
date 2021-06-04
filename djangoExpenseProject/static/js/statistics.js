const renderChart=(labels,data)=>{
  var ctx = document.getElementById('expensesChart');
  var expensesChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        label: 'Last six months expenses',
        data: data,
        backgroundColor: [
          'rgba(255, 99, 132, 0.2)',
          'rgba(54, 162, 235, 0.2)',
          'rgba(255, 206, 86, 0.2)'
        ],
        borderColor: [
          'rgba(255,99,132,1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)'
        ],
        borderWidth: 1,
      }],
    },
    options: {
      title: {
        display: true,
        text: "Expenses per category",
      },
    },
  });
}

// listener when document load complete
const getChartData=()=>{
  fetch('/expenses-category-summary')
      .then((res) => res.json())
      .then((results) => {
    console.log("results", results);
    //decode the data
    const category_data = results.expense_category_data;
    console.log(category_data);

    const [labels, data] = [
        Object.keys(category_data),
        Object.values(category_data),
    ]
    renderChart(labels,data);
  });
  //document.onload=getChartData();
};
document.onload=getChartData();
