# coding: utf-8

from flask.ext.babel import Babel
import flask

import config
import util

app = flask.Flask(__name__)
app.config.from_object(config)
app.jinja_env.line_statement_prefix = '#'
app.jinja_env.line_comment_prefix = '##'
app.jinja_env.globals.update(
    check_form_fields=util.check_form_fields,
    is_iterable=util.is_iterable,
    slugify=util.slugify,
    update_query_argument=util.update_query_argument,
  )
app.config['BABEL_DEFAULT_LOCALE'] = config.LOCALE_DEFAULT
babel = Babel(app)

import auth
import control
import model
import task

from api import helpers
api_v1 = helpers.Api(app, prefix='/api/v1')

import api.v1


if config.DEVELOPMENT:
  from werkzeug import debug
  app.wsgi_app = debug.DebuggedApplication(app.wsgi_app, evalex=True)
  app.testing = False


@flask.request_started.connect_via(app)
def request_started(sender, **extra):
  flask.request.country = None
  flask.request.region = None
  flask.request.city = None
  flask.request.city_lat_lng = '40.6393495,22.944606399999998'
  if 'X-AppEngine-Country' in flask.request.headers:
    flask.request.country = flask.request.headers['X-AppEngine-Country']
  if 'X-AppEngine-Region' in flask.request.headers:
    flask.request.region = flask.request.headers['X-AppEngine-Region']
  if 'X-AppEngine-City' in flask.request.headers:
    flask.request.city = flask.request.headers['X-AppEngine-City']
  if 'X-AppEngine-CityLatLong' in flask.request.headers:
    flask.request.city_lat_lng = flask.request.headers['X-AppEngine-CityLatLong']
