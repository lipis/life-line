window.init_trips = ->
  setTimeout ->
    if not window.location.hash
      window.scrollTo 0, document.body.scrollHeight
  , 100

  window.chart = new ChartMap 'line'

  if location.hash.length > 2
    $(".#{location.hash.substr(1)}").addClass('active')
