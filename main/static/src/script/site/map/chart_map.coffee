class window.ChartMap
  constructor: (@type='countries') ->
    @event_dbs = []

    @countries = []
    @countries_data = [['Country', 'Visits']]
    @cities = []
    @cities_data = [['City', 'Visits']]

    @host = document.getElementById('map')
    @chart = null
    @gmap = null
    @bounds = new google.maps.LatLngBounds()
    @type == 'countries'
    @service_url = $(@host).data('service-url') or '/_s/place/'
    @load()

    @init_toolbar()

  init_toolbar: () =>
    $("#map-toolbar input[value=#{@type}]").parent().click()

    $('#map-toolbar input[name=type]').change () =>
      @type = $('#map-toolbar input[name=type]:checked').val()
      @draw()

  load: () =>
    service_call 'GET', @service_url, @on_event_result_callback


  on_loaded: =>
    @normalize_data()
    @draw()


  draw: () =>
    if @type == 'countries'
      @draw_countries()
    if @type == 'cities'
      @draw_cities()
    if @type == 'line' and @type != @last_type
      @draw_line()
    @last_type = @type


  draw_chart: (data=@countries_data, displayMode='area', region='world') =>
    data = google.visualization.arrayToDataTable data
    options =
      displayMode: displayMode
      region: region
      colorAxis:
        colors: [
          '#c6e2f6'
          '#1e7cc1'
        ]
    @chart = new google.visualization.GeoChart @host
    @chart.draw data, options


  draw_countries: (region) =>
    @type = 'countries'
    @draw_chart @countries_data, 'area', region


  draw_cities: (region) =>
    @type = 'cities'
    @draw_chart @cities_data, 'markers', region


  draw_line: () =>
    @type = 'line'
    options =
      zoom: 2
      mapTypeId: google.maps.MapTypeId.TERRAIN

    @gmap = new google.maps.Map @host, options

    color = new one.color '#f00'
    max = .7
    for i in [0..@event_dbs.length - 1]
      percentage = i / (@event_dbs.length - 1)
      if i < @event_dbs.length - 1
        new google.maps.Polyline
          path: [@event_dbs[i].google_maps_point, @event_dbs[i + 1].google_maps_point]
          strokeColor: color.lightness(max - (i / @event_dbs.length) * max).hex()
          strokeOpacity: (1 - percentage * .5) * .7
          strokeWeight: 2
          geodesic: true
          map: @gmap

      if not @event_dbs[i].layover
        new google.maps.Marker
          position: @event_dbs[i].google_maps_point
          map: @gmap
          icon:
            path: google.maps.SymbolPath.CIRCLE
            scale: 2

    @gmap.fitBounds @bounds


  normalize_data: =>
    for event_db in @event_dbs
      if event_db.layover
        continue
      if @countries[event_db.country]
        @countries[event_db.country] += 1
      else
        @countries[event_db.country] = 1

      event_db.city_country = "#{event_db.place}, #{event_db.country}"
      if @cities[event_db.city_country]
        @cities[event_db.city_country] += 1
      else
        @cities[event_db.city_country] = 1

    for country of @countries
      @countries_data.push [country, @countries[country]]

    for city of @cities
      @cities_data.push [city, @cities[city]]


  on_event_result_callback: (err, event_dbs, more) =>
    return onerror(err) if err
    for event_db in event_dbs
      latlng = event_db.geo_pt.split ','
      event_db.google_maps_point = new google.maps.LatLng latlng[0], latlng[1]
      @bounds.extend event_db.google_maps_point
      @event_dbs.push event_db
    if more
      more @on_event_result_callback
    else
      @on_loaded()
