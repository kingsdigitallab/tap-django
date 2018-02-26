function chart(dataUrl, chartElement, chartTitle, chartId) {
  var colours = [
    '#9e0142',
    '#d53e4f',
    '#f46d43',
    '#fdae61',
    '#fee08b',
    '#ffffbf',
    '#e6f598',
    '#abdda4',
    '#66c2a5',
    '#3288bd',
    '#5e4fa2'
  ]

  $.getJSON(dataUrl, function(data) {
    var ctx = $(chartElement)
    var charType = 'bar'
    var labels = []
    var datasetsObj = {}
    var values = []
    var datasets = []
    var scales = {}

    if (data.length > 1 && data.length < 4) {
      charType = 'doughnut'
    }

    for (var i = 0; i < data.length; i++) {
      data[i].id = data[i]._id

      var el = data[i].id
      if (el.id) {
        labels.push(el.value)

        if (!(el.id in datasetsObj)) {
          datasetsObj[el.id] = {}
          datasetsObj[el.id].label = el.id
          datasetsObj[el.id].backgroundColor =
            colours[Object.keys(datasetsObj).length - 1]
          datasetsObj[el.id].data = []
        }
        datasetsObj[el.id].data.push(data[i].value)
      } else {
        labels.push(data[i].id)
        values.push(data[i].value)
      }

      delete data[i]._id
    }

    if ($.isEmptyObject(datasetsObj)) {
      datasets = [
        {
          label: chartTitle,
          backgroundColor: colours,
          borderColor: colours,
          data: values
        }
      ]
    } else {
      labels = Array.from(new Set(labels))

      for (var key in datasetsObj) {
        datasets.push(datasetsObj[key])
      }

      scales = {
        xAxes: [
          {
            stacked: true
          }
        ],
        yAxes: [
          {
            stacked: true
          }
        ]
      }
    }

    var chart = new Chart(ctx, {
      type: charType,
      data: {
        labels: labels,
        datasets: datasets
      },
      options: {
        responsive: true,
        scales: scales
      }
    })
  }).fail(function() {
    alert('error')
  })
}
