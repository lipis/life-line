window.init_event_list = () ->
  window.chart = new ChartMap 'line'

  if location.hash.length > 2
    $(".#{location.hash.substr(1)}").addClass('info')

window.init_event_update = () ->
  init_places_click()
  init_dates_click()
  init_search_input()

  update_datetime()

  $year_option = $($('#year option')[0])
  $year_option.html "#{$year_option.html()} &#8226;"

  $('#month').val $('#month').data 'selected'
  $('#day').val $('#day').data 'selected'

  $('.datetime').change update_datetime
  $('.datetime').blur update_datetime
  $('.datetime').focus update_datetime
  $('#year').focus()

  $('#layover').click () ->
    window.layover_clicked = true


update_datetime = () ->
  year_val = parseInt $('#year').val() or 0
  month_val = parseInt $('#month').val() or 0
  day_val = parseInt $('#day').val() or 0

  $('#month').prop('disabled', year_val == 0)
  $('#day').prop('disabled', month_val == 0)

  # should work without that line..
  moment.locale LOCALE

  date = moment.utc [year_val]
  if month_val > 0
    date = moment.utc [year_val, month_val - 1]

  if date.isValid()
    $('#month').empty()
    $('#month').append "<option value='0'>----</option>"
    for m in [0 .. 11]
      current = moment([year_val, m])
      today = if moment().year() == current.year() and moment().month() == current.month() then '&#8226;' else ''
      $('#month').append "<option value='#{m + 1}'>#{current.format('MMMM')} #{today}</option>"
    $('#month').val month_val

    $('#day').empty()
    $('#day').append "<option value='0'>----</option>"
    for d in [1 .. date.daysInMonth()]
      current = moment([year_val, month_val - 1, d])

      if d == 1
        $('#day').append "<optgroup>"
      else if current.day() == 1
        $('#day').append "</optgroup><optgroup>"
      else if d == date.daysInMonth()
        $('#day').append "</optgroup>"

      today = if moment().year() == current.year() and moment().month() == current.month() and moment().date() == current.date() then '&#8226;' else ''
      $('#day').append "<option value='#{d}'>#{d} #{current.format('ddd')} #{today}</option>"
    $('#day').val if month_val == 0 then 0 else day_val


window.search_map = (query, fit) ->
  $('.error-block', '.search-group').hide()
  $('.description', '.search-group').text('Searching...')
  $('.search-group').removeClass('has-error')

  window.ignore_geocode = true
  geocoder_map.geocode_address query, fit, (error, result) ->
    window.ignore_geocode = false
    if error
      $('.description', '.search-group').text('Nothing found... Try again!')
      $('.search-group').addClass('has-error')
      return
    $('.description', '.search-group').text("#{result.address}")
    $('#address').val result.address
    $('#place').val result.place
    $('#country').val result.country
    $('#country_code').val result.country_code
    $('#lat').val result.lat
    $('#lng').val result.lng
    $('#lng').val result.lng

    if not window.layover_clicked
      $('#layover').prop 'checked', result.layover


window.search_with_timer = (timeout=500) ->
  if search_timeout
    clearTimeout search_timeout
  search_timeout = setTimeout ->
      search_map $('#search').val(), true
    , timeout


window.init_search_input = ->
  window.geocoder_map = new GeocoderMap $('#lat').val(), $('#lng').val()
  window.timer = null
  google.maps.event.addListener geocoder_map.gmap, 'drag', ->
    return if window.ignore_geocode

    if timer
      clearTimeout timer
    window.timer = setTimeout ->
        search_map "#{geocoder_map.gmap.getCenter().lat()},#{geocoder_map.gmap.getCenter().lng()}"
      , 800

  $('#search').keypress (e) ->
    if e.keyCode == 13
      search_with_timer 0
      $('#search').select()
      e.preventDefault()

  window.search_timeout = null

  $('#search').keyup () ->
    search_with_timer()

  $('#search').change () ->
    search_with_timer()


window.init_places_click = ->
  $('.place').click (e) ->
    e.preventDefault()
    $('#search').val $(e.currentTarget).text()
    $('#search').focus()
    $('#search').select()
    search_with_timer()


window.init_dates_click = ->
  $('.today').click (e) ->
    e.preventDefault()
    today = moment()
    $('#year').val today.year()
    $('#month').val today.month() + 1
    $('#day').val today.date()
    $('#hour').val 0
    update_datetime()

  $('.now').click (e) ->
    e.preventDefault()
    today = moment()
    $('#hour').val today.hour()
