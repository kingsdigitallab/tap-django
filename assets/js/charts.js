var colourSchemes = ['tol-dv', 'tol-sq', 'tol-rainbow']

var chart = function(dataUrl, chartElement, chartTitle, chartId, queryField) {
  $.getJSON(dataUrl, function(data) {
    var ctx = $(chartElement)
    var colours = chartJsColours(palette(colourSchemes, data.length, 0))

    var charType = 'bar'

    var labels = []
    var datasetsObj = {}
    var values = []
    var datasets = []
    var scales = {}

    // if (data.length > 1 && data.length < 4) {
    //   charType = 'doughnut'
    // }

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
          data: values
        }
      ]
    } else {
      charType = 'bar'
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

    if (queryField) {
      $(ctx).hover(function(evt) {
        $(ctx).css('cursor', 'pointer')
      })
      $(ctx).click(function(evt) {
        var item = chart.getElementAtEvent(evt)[0]

        if (item) {
          var label = chart.data.labels[item._index]
          var value = chart.data.datasets[item._datasetIndex].data[item._index]
          location.href =
            '?query-field=' +
            queryField +
            '&query-value=' +
            encodeURIComponent(label)
        }
      })
    }
  }).fail(function() {
    alert('error')
  })
}

var chartJsColours = function(colors) {
  return colors.map(function(color) {
    return '#' + color
  })
}

var wordcloud = function(dataUrl, chartElementId) {
  var $el = $('#' + chartElementId)
  var width = $el.parent().width()
  var viewportHeight = window.innerHeight
  var height = width < viewportHeight ? width : viewportHeight

  $.getJSON(dataUrl, function(data) {
    WordCloud(chartElementId, {
      list: data,
      backgroundColor: '#f0f0f0',
      color: 'random-dark',
      gridSize: 8,
      weightFactor: 0.1,
      width: width
    })
  }).fail(function() {
    alert('error')
  })

  $el.on('wordcloudstop', function wordcloudstopped(evt) {
    $('#wordcloud span').click(function() {
      location.href =
        '?query-field=chirp.words&query-value=' +
        encodeURIComponent(this.textContent)
    })
  })
}
