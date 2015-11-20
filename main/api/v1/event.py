# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb
from flask.ext import restful
import flask

from api import helpers
import auth
import model
import util

from main import api_v1


@api_v1.resource('/user/<username>/event/', endpoint='api.user.event.list')
@api_v1.resource('/event/', endpoint='api.event.list')
class EventListAPI(restful.Resource):
  def get(self, username=None):
    if auth.is_logged_in():
      user_db = auth.current_user_db()
    else:
      user_dbs, user_cursor = model.User.get_dbs(is_public=True, limit=10)
      user_db = random.choice(user_dbs) if user_dbs else None

    if username and user_db.username != username:
      if not user_db.admin:
        helpers.make_not_found_exception('User %s not found' % username)
      user_db = model.User.get_by('username', username)

    if not user_db:
      helpers.make_not_found_exception('User not found')

    event_dbs, event_cursor = user_db.get_event_dbs()
    return helpers.make_response(event_dbs, model.Event.FIELDS, event_cursor)


@api_v1.resource('/event/<string:event_key>/', endpoint='api.event')
class EventAPI(restful.Resource):
  @auth.login_required
  def get(self, event_key):
    event_db = ndb.Key(urlsafe=event_key).get()
    if not event_db or event_db.user_key != auth.current_user_key():
      return helpers.make_not_found_exception('Event %s not found' % event_key)
    return helpers.make_response(event_db, model.Event.FIELDS)



###############################################################################
# Admin
###############################################################################
@api_v1.resource('/admin/event/', endpoint='api.admin.event.list')
class AdminEventListAPI(restful.Resource):
  @auth.admin_required
  def get(self):
    event_keys = util.param('event_keys', list)
    if event_keys:
      event_db_keys = [ndb.Key(urlsafe=k) for k in event_keys]
      event_dbs = ndb.get_multi(event_db_keys)
      return helpers.make_response(event_dbs, model.event.FIELDS)

    event_dbs, event_cursor = model.Event.get_dbs()
    return helpers.make_response(event_dbs, model.Event.FIELDS, event_cursor)


@api_v1.resource('/admin/event/<string:event_key>/', endpoint='api.admin.event')
class AdminEventAPI(restful.Resource):
  @auth.admin_required
  def get(self, event_key):
    event_db = ndb.Key(urlsafe=event_key).get()
    if not event_db:
      helpers.make_not_found_exception('Event %s not found' % event_key)
    return helpers.make_response(event_db, model.Event.FIELDS)
