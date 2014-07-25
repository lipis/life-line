# -*- coding: utf-8 -*-

from google.appengine.ext import ndb

from flask.ext import wtf
from flask.ext.babel import lazy_gettext as _
import flask

from datetime import datetime

import auth
import i18n
import model
import util
import task

from main import app


HOURS = []
for hour in range(24):
  HOURS.append((str(hour), '%02d:00' % hour))

HOURS[0] = ('0', '----')


class EventUpdateForm(i18n.Form):
  search = wtf.TextField(_('Search for a place'), [wtf.validators.optional()], description=_('Paralia Armenistis, Chalkidiki'))
  address = wtf.TextField(_('Name / Address (Automatic)'), [wtf.validators.required()])
  place = wtf.TextField(_('Place / City (Automatic)'), [wtf.validators.required()])
  country = wtf.TextField(_('Country (Automatic)'), [wtf.validators.required()])
  country_code = wtf.HiddenField('Country Code', [wtf.validators.required()])
  lat = wtf.HiddenField('Latitude', [wtf.validators.required()])
  lng = wtf.HiddenField('Longtitude', [wtf.validators.required()])
  timestamp = wtf.TextField(_('Timestamp'), [wtf.validators.optional()])
  notes = wtf.TextAreaField(_('Notes'), [wtf.validators.optional()])
  layover = wtf.BooleanField(_('This place is a layover'), [wtf.validators.optional()])
  add_more = wtf.BooleanField(_('Add More'), [wtf.validators.optional()])

  year = wtf.SelectField(_('Year'), [wtf.validators.optional()])
  month = wtf.TextField(_('Month'), [wtf.validators.optional()])
  day = wtf.TextField(_('Day'), [wtf.validators.optional()])
  hour = wtf.SelectField(_('Time'), [wtf.validators.optional()], choices=HOURS)


@app.route('/place/add/', methods=['GET', 'POST'])
@app.route('/place/<int:event_id>/update/', methods=['GET', 'POST'], endpoint='event_update')
@auth.login_required
def event_create(event_id=0):
  country = None
  region = None
  city = None
  city_lat_lng = '40.6393495,22.944606399999998'
  if 'X-AppEngine-Country' in flask.request.headers:
    country = flask.request.headers['X-AppEngine-Country']
  if 'X-AppEngine-Region' in flask.request.headers:
    region = flask.request.headers['X-AppEngine-Region']
  if 'X-AppEngine-City' in flask.request.headers:
    city = flask.request.headers['X-AppEngine-City']
  if 'X-AppEngine-CityLatLong' in flask.request.headers:
    city_lat_lng = flask.request.headers['X-AppEngine-CityLatLong']

  if event_id == 0:
    event_db = model.Event(user_key=auth.current_user_key())
  else:
    event_db = model.Event.get_by_id(event_id)

  form = EventUpdateForm(obj=event_db)
  today = datetime.utcnow().date()
  today = datetime(today.year, today.month, today.day)
  form.year.choices = sorted([(str(y), y) for y in range(1900, today.year + 1)], reverse=True)

  if form.validate_on_submit():
    event_db.search = form.search.data
    success = False

    form.year.data = int(form.year.data)
    form.month.data = int(form.month.data)
    try:
      form.day.data = int(form.day.data)
    except:
      form.day.data = 1

    if not form.year.data:
      form.timestamp.errors.append(_('You should at least enter a year'))
    else:
      month = 1
      day = 1

      if form.month.data and form.day.data:
        month = form.month.data
        day = form.day.data
      elif form.month.data:
        month = form.month.data
        day = 1
      else:
        month = 1
        day = 1

      hour = int(form.hour.data) or 0
      try:
        event_db.timestamp = datetime(form.year.data, month, day, hour)
        success = True
      except:
        form.timestamp.errors.append(_('Enter a valid date'))
        success = False

    if success:
      if form.month.data and form.day.data:
        event_db.accuracy = 'day'
      elif form.month.data:
        event_db.accuracy = 'month'
      else:
        event_db.accuracy = 'year'

      event_db.address = form.address.data
      event_db.country = form.country.data
      event_db.country_code = form.country_code.data
      event_db.geo_pt = ndb.GeoPt(form.lat.data, form.lng.data)
      event_db.layover = form.layover.data
      event_db.notes = form.notes.data
      event_db.place = form.place.data
      event_db.put()
      if event_id:
        flask.flash('"%s" is updated!' % event_db.address, category='success')
      else:
        flask.flash('"%s" is added!' % event_db.address, category='success')
        task.new_event_notification(event_db)

      if form.add_more.data:
        return flask.redirect(flask.url_for('event_create'))
      return flask.redirect('%s#%d' % (flask.url_for('event_list'), event_db.key.id()))

  if not form.errors:
    form.add_more.data = event_id == 0
    form.lat.data = '0'
    form.lng.data = '0'

    if event_db.geo_pt:
      form.lat.data = event_db.geo_pt.lat
      form.lng.data = event_db.geo_pt.lon
    elif city_lat_lng:
      form.lat.data = city_lat_lng.split(',')[0]
      form.lng.data = city_lat_lng.split(',')[1]

    try:
      form.year.data = str(event_db.timestamp.year)
      if event_db.accuracy == 'month':
        form.month.data = str(event_db.timestamp.month)
      elif event_db.accuracy == 'day':
        form.month.data = str(event_db.timestamp.month)
        form.day.data = str(event_db.timestamp.day)
      form.hour.data = str(event_db.timestamp.hour)

    except:
      pass

  return flask.render_template(
      'event/event_update.html',
      html_class='event-update',
      title=u'%s' % (_('Add Place') if event_id == 0 else '%s, %s' % (event_db.place, event_db.country)),
      form=form,
      today=today,
      event_db=event_db,
      country=country,
      region=region,
      city=city,
      city_lat_lng=city_lat_lng,
    )


@app.route('/_s/user/<username>/event/', endpoint='event_list_service')
@app.route('/user/<username>/event/')
@app.route('/_s/place/')
@app.route('/place/')
@auth.login_required
def event_list(username=None):
  user_db = auth.current_user_db()
  if username and user_db.username != username:
    if not user_db.admin:
      return flask.abort(404)
    user_db = model.User.get_by('username', username)
    if not user_db:
      return flask.abort(404)

  event_dbs, next_cursor = user_db.get_event_dbs()

  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_dbs(event_dbs, next_cursor)

  return flask.render_template(
      'event/event_list.html',
      html_class='event-list',
      title=_('My Places'),
      event_dbs=event_dbs,
      next_url=util.generate_next_url(next_cursor),
      has_json=True,
      user_db=user_db,
    )
