$ ->
  init_common()
  init_map_common()

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
