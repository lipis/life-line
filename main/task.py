# coding: utf-8

import flask
from google.appengine.api import mail
from google.appengine.ext import deferred

import config


###############################################################################
# Helpers
###############################################################################
def send_mail_notification(subject, body, **kwargs):
  if not config.CONFIG_DB.feedback_email:
    return
  brand_name = config.CONFIG_DB.brand_name
  sender = '%s <%s>' % (brand_name, config.CONFIG_DB.feedback_email)
  subject = '[%s] %s' % (brand_name, subject)
  deferred.defer(mail.send_mail, sender, sender, subject, body, **kwargs)


###############################################################################
# User related
###############################################################################
def new_user_notification(user_db):
  if not config.CONFIG_DB.notify_on_new_user:
    return
  body = 'name: %s\nusername: %s\nemail: %s\n%s\n%s' % (
      user_db.name,
      user_db.username,
      user_db.email,
      ''.join([': '.join(('%s\n' % a).split('_')) for a in user_db.auth_ids]),
      flask.url_for('user_update', user_id=user_db.key.id(), _external=True),
    )
  send_mail_notification('New user: %s' % user_db.name, body)


###############################################################################
# Event related
###############################################################################
def new_event_notification(event_db):

  user_db = event_db.user_key.get()

  body = 'name: %s\nusername: %s\ncountry: %s\nplace: %s\n' % (
      user_db.name,
      user_db.username,
      event_db.country,
      event_db.place
    )
  send_mail_notification('New event: %s' % event_db.address, body)
