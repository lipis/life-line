$ ->
  init_common()
  on_resize()
  $(window).resize on_resize

on_resize = ->
  height = $(window).height() - $('.navbar-fixed-top').outerHeight() - ($('#map-toolbar')?.outerHeight() or 0)
  if $('html.event-list').length > 0
    height -= 20
  if height > parseInt($('.map').data('max-height'))
    height = parseInt($('.map').data('max-height'))

  $('.map').height height
  chart?.draw()


$ -> $('html.welcome').each ->
  init_welcome()

$ -> $('html.profile').each ->
  init_profile()

$ -> $('html.signin').each ->
  init_signin()

$ -> $('html.feedback').each ->

$ -> $('html.user-list').each ->
  init_user_list()

$ -> $('html.user-merge').each ->
  init_user_merge()

$ -> $('html.admin-config').each ->
  init_admin_config()

$ -> $('html.event-list').each ->
  init_event_list()

$ -> $('html.event-update').each ->
  init_event_update()
