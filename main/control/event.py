# -*- coding: utf-8 -*-

from datetime import datetime
import random
import copy

from flask.ext import wtf
from flask.ext.babel import lazy_gettext as _
from google.appengine.ext import ndb
import flask
import wtforms

import auth
import i18n
import model
import util
import iso

from main import app


HOURS = []
for hour in range(24):
  HOURS.append((str(hour), '%02d:00' % hour))

HOURS[0] = ('0', '----')


class EventUpdateForm(i18n.Form):
  search = wtforms.TextField(_('Search for a place'), [wtforms.validators.optional()])
  address = wtforms.TextField(_('Name / Address (Automatic)'), [wtforms.validators.required()])
  place = wtforms.TextField(_('Place / City (Automatic)'), [wtforms.validators.required()])
  country = wtforms.TextField(_('Country (Automatic)'), [wtforms.validators.required()])
  country_code = wtforms.HiddenField('Country Code', [wtforms.validators.required()])
  lat = wtforms.HiddenField('Latitude', [wtforms.validators.required()])
  lng = wtforms.HiddenField('Longtitude', [wtforms.validators.required()])
  timestamp = wtforms.TextField(_('Timestamp'), [wtforms.validators.optional()])
  notes = wtforms.TextAreaField(_('Notes'), [wtforms.validators.optional()])
  layover = wtforms.BooleanField(_('This place is a layover'), [wtforms.validators.optional()])
  add_more = wtforms.BooleanField(_('Add More'), [wtforms.validators.optional()])
  home = wtforms.BooleanField(model.Event.home._verbose_name, [wtforms.validators.optional()])

  year = wtforms.SelectField(_('Year'), [wtforms.validators.optional()])
  month = wtforms.TextField(_('Month'), [wtforms.validators.optional()])
  day = wtforms.TextField(_('Day'), [wtforms.validators.optional()])
  hour = wtforms.SelectField(_('Time'), [wtforms.validators.optional()], choices=HOURS)


@app.route('/place/add/', methods=['GET', 'POST'])
@app.route('/place/<int:event_id>/update/', methods=['GET', 'POST'], endpoint='event_update')
@auth.login_required
def event_create(event_id=0):
  if event_id == 0:
    event_db = model.Event(user_key=auth.current_user_key())
  else:
    event_db = model.Event.get_by_id(event_id)

  if not event_db or event_db.user_key != auth.current_user_key():
    return flask.abort(404)

  form = EventUpdateForm(obj=event_db)
  today = datetime.utcnow().date()
  today = datetime(today.year, today.month, today.day)
  form.year.choices = sorted([(str(y), y) for y in range(1900, today.year + 1)], reverse=True)

  if form.validate_on_submit():
    form.year.data = int(form.year.data)
    form.month.data = int(form.month.data)
    try:
      form.day.data = int(form.day.data)
    except:
      form.day.data = 1

    success = False

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
        form.timestamp.data = datetime(form.year.data, month, day, hour)
        success = True
      except:
        form.timestamp.errors.append(_('Enter a valid date'))
        success = False

    if success:
      form.populate_obj(event_db)

      if form.month.data and form.day.data:
        event_db.accuracy = 'day'
      elif form.month.data:
        event_db.accuracy = 'month'
      else:
        event_db.accuracy = 'year'
      event_db.geo_pt = ndb.GeoPt(form.lat.data, form.lng.data)
      event_db.put()
      if event_id:
        flask.flash('"%s" is updated!' % event_db.address, category='success')
      else:
        flask.flash('"%s" is added!' % event_db.address, category='success')

      if form.add_more.data:
        timestamp = event_db.timestamp.strftime('%Y%H')
        if event_db.accuracy == 'month':
          timestamp = event_db.timestamp.strftime('%Y%m%H')
        if event_db.accuracy == 'day':
          timestamp = event_db.timestamp.strftime('%Y%m%d%H')

        return flask.redirect(flask.url_for('event_create', timestamp=timestamp))
      return flask.redirect('%s#%d' % (flask.url_for('trips'), event_db.key.id()))

  if not form.errors:
    form.add_more.data = event_id == 0
    form.lat.data = '0'
    form.lng.data = '0'

    if event_db.geo_pt:
      form.lat.data = event_db.geo_pt.lat
      form.lng.data = event_db.geo_pt.lon
    elif flask.request.city_lat_lng:
      form.lat.data = flask.request.city_lat_lng.split(',')[0]
      form.lng.data = flask.request.city_lat_lng.split(',')[1]

    try:
      if event_id == 0:
        timestamp = util.param('timestamp')
        form.year.data = timestamp[:4].lstrip('0')
        form.hour.data = timestamp[-2:].lstrip('0')
        if len(timestamp) == 8:
          form.month.data = timestamp[4:-2].lstrip('0')
        if len(timestamp) == 10:
          form.month.data = timestamp[4:-4].lstrip('0')
          form.day.data = timestamp[6:-2].lstrip('0')
      else:
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
    )


@app.route('/user/<username>/countries/')
@app.route('/countries/')
@auth.login_required
def countries(username=None):
  user_db = auth.current_user_db()
  if username and user_db.username != username:
    if not user_db.admin:
      return flask.abort(404)
    user_db = model.User.get_by('username', username)
    if not user_db:
      return flask.abort(404)

  event_dbs, next_cursor = user_db.get_event_dbs(
      order='timestamp,accuracy,created', limit=-1
    )

  country_dbs_ = {}
  country = {
    'country_code': '',
    'seconds': 0,
    'current': False,
  }
  last_event_db = None

  for event_db in event_dbs:
    if event_db.layover:
      continue
    if last_event_db:
      if last_event_db.country_code not in country_dbs_:
        country_dbs_[last_event_db.country_code] = copy.copy(country)
        country_dbs_[last_event_db.country_code]['country_code'] = last_event_db.country_code
      country_dbs_[last_event_db.country_code]['seconds'] += (event_db.timestamp - last_event_db.timestamp).total_seconds()
    last_event_db = event_db

  # current country
  if last_event_db:
    if last_event_db.country_code not in country_dbs_:
      country_dbs_[last_event_db.country_code] = copy.copy(country)
      country_dbs_[last_event_db.country_code]['country_code'] = last_event_db.country_code
    country_dbs_[last_event_db.country_code]['seconds'] += (datetime.utcnow() - last_event_db.timestamp).total_seconds()
    country_dbs_[last_event_db.country_code]['current'] = True


  country_dbs = []
  total = 0

  for country_code in country_dbs_:
    country = country_dbs_[country_code]
    country['seconds'] = int(country['seconds'])
    country['hours'] = int(country['seconds'] / 60 / 60)
    country['days'] = int(round(country['seconds'] / 60 / 60 / 24))
    country['months'] = country['days'] / 30.0
    country['years'] = country['days'] / 365.0
    country['country'] = iso.ISO_3166[country['country_code']]
    country_dbs.append(country)
    total += country['seconds']

  country_dbs = sorted(country_dbs, key=lambda c: c['seconds'], reverse=True)
  return flask.render_template(
      'event/stats.html',
      html_class='stats countries',
      title=_('My Stats'),
      event_dbs=event_dbs,
      country_dbs=country_dbs,
      total=total,
      next_url=util.generate_next_url(next_cursor),
      user_db=user_db,
    )


@app.route('/user/<username>/trips/')
@app.route('/trips/')
@auth.login_required
def trips(username=None):
  user_db = auth.current_user_db()
  if username and user_db.username != username:
    if not user_db.admin:
      return flask.abort(404)
    user_db = model.User.get_by('username', username)
    if not user_db:
      return flask.abort(404)

  event_dbs, next_cursor = user_db.get_event_dbs(limit=-1, order='timestamp,-accuracy,created')

  return flask.render_template(
      'event/trips.html',
      html_class='trips',
      title=_('My Trips'),
      event_dbs=event_dbs,
      next_url=util.generate_next_url(next_cursor),
      user_db=user_db,
    )


@app.route('/user/<username>/places/')
@app.route('/places/')
@auth.login_required
def places(username=None):
  user_db = auth.current_user_db()
  if username and user_db.username != username:
    if not user_db.admin:
      return flask.abort(404)
    user_db = model.User.get_by('username', username)
    if not user_db:
      return flask.abort(404)

  event_dbs, next_cursor = user_db.get_event_dbs(
      order='timestamp,accuracy,created', limit=-1
    )

  place_dbs_ = {}
  country = {
    'country_code': '',
    'city': '',
    'seconds': 0,
    'current': False,
  }
  last_event_db = None

  for event_db in event_dbs:
    if event_db.layover:
      continue
    if last_event_db:
      if last_event_db.place not in place_dbs_:
        place_dbs_[last_event_db.place] = copy.copy(country)
        place_dbs_[last_event_db.place]['country_code'] = last_event_db.country_code
        place_dbs_[last_event_db.place]['place'] = last_event_db.place
      place_dbs_[last_event_db.place]['seconds'] += (event_db.timestamp - last_event_db.timestamp).total_seconds()
    last_event_db = event_db

  # current country
  if last_event_db:
    if last_event_db.place not in place_dbs_:
      place_dbs_[last_event_db.place] = copy.copy(country)
      place_dbs_[last_event_db.place]['country_code'] = last_event_db.country_code
      place_dbs_[last_event_db.place]['place'] = last_event_db.place
    place_dbs_[last_event_db.place]['seconds'] += (datetime.utcnow() - last_event_db.timestamp).total_seconds()
    place_dbs_[last_event_db.place]['current'] = True


  place_dbs = []
  total = 0

  for place in place_dbs_:
    place = place_dbs_[place]
    place['seconds'] = int(place['seconds'])
    place['hours'] = int(place['seconds'] / 60 / 60)
    place['days'] = int(round(place['seconds'] / 60 / 60 / 24))
    place['months'] = place['days'] / 30.0
    place['years'] = place['days'] / 365.0
    place['country'] = iso.ISO_3166[place['country_code']]
    place_dbs.append(place)
    total += place['seconds']

  place_dbs = sorted(place_dbs, key=lambda c: c['seconds'], reverse=True)
  return flask.render_template(
      'event/stats2.html',
      html_class='stats places',
      title=_('My Stats'),
      event_dbs=event_dbs,
      place_dbs=place_dbs,
      total=total,
      next_url=util.generate_next_url(next_cursor),
      user_db=user_db,
    )


