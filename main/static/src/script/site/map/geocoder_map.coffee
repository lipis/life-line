class window.GeocoderMap
  constructor: (lat, lng) ->
    @dest_longitude = undefined
    @dest_latitude = undefined

    @geocoder = new google.maps.Geocoder()
    latlng = new google.maps.LatLng(lat, lng)
    options =
      zoom: 9
      center: latlng
      mapTypeId: google.maps.MapTypeId.ROADMAP

    @gmap = new google.maps.Map($('#event-map')[0], options)

    @marker = new google.maps.Marker
      map: @gmap

    @marker.bindTo 'position', @gmap, 'center'


  add_marker: (location) =>
    if @marker?
      @marker.setMap null
      @marker = `undefined`
    @marker = new google.maps.Marker
      position: location
      map: @gmap

  geocode_address: (address, fit, callback) =>
    @geocoder.geocode
      address: address
    , (results, status) =>
      if status is google.maps.GeocoderStatus.OK
        if fit
          @gmap.fitBounds results[0].geometry.viewport
        callback? undefined, @process_result results
      else
        callback? status

  process_result: (results) =>
    res =
      layover: false
    LOG 'Results', results

    for type in results[0].types
      if type in ['transit_station', 'airport', 'bus_station', 'train_station']
        res['layover'] = true
        break

    result = results[0]

    res['address'] = result.formatted_address
    res['lat'] = result.geometry.location.lat()
    res['lng'] = result.geometry.location.lng()

    for component in result.address_components
      name = component.long_name or component.short_name
      for type in component.types
        res[type] = name
        if type == 'country'
          res['country_code'] = component.short_name or ''

    res['place'] = res.locality or res.natural_feature or res.administrative_area_level_3 or res.administrative_area_level_2 or res.administrative_area_level_1
    delete res.political?
    LOG 'Final result', res
    return res
