$ ->
  init_common()
  init_map_common()

$ -> $('html.welcome').each ->
  init_welcome()

$ -> $('html.auth').each ->
  init_auth()

$ -> $('html.feedback').each ->

$ -> $('html.user-list').each ->
  init_user_list()

$ -> $('html.user-merge').each ->
  init_user_merge()

$ -> $('html.admin-config').each ->
  init_admin_config()

$ -> $('html.event-update').each ->
  init_event_update()

$ -> $('html.trips').each ->
  init_trips()
