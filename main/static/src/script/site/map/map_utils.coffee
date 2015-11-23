window.init_map_common = ->
  $(window).resize ->
    height = $(window).height() - $('.navbar-fixed-top').outerHeight() - ($('#map-toolbar')?.outerHeight() or 0)
    if $('html.trips').length > 0
      height -= 20
    if height > parseInt($('.map').data('max-height'))
      height = parseInt($('.map').data('max-height'))

    $('.map').height height
    chart?.draw()

  $(window).resize()
