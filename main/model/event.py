# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb

from api import fields
import model
import util


class Event(model.Base):
  user_key = ndb.KeyProperty(kind=model.User, required=True)
  search = ndb.StringProperty(default='')
  address = ndb.StringProperty(required=True)
  place = ndb.StringProperty(required=True)
  country = ndb.StringProperty(required=True)
  country_code = ndb.StringProperty(required=True)
  geo_pt = ndb.GeoPtProperty()
  layover = ndb.BooleanProperty(default=False)
  timestamp = ndb.DateTimeProperty()
  accuracy = ndb.StringProperty(default='year', choices=['year', 'month', 'day'])
  notes = ndb.StringProperty(default='')
  home = ndb.BooleanProperty(default=False, verbose_name='This is my new home or base')

  @ndb.ComputedProperty
  def name_short(self):
    return ', '.join([self.place, self.country])

  @ndb.ComputedProperty
  def name_tax(self):
    return ' - '.join([self.place, self.country_code])

  @ndb.ComputedProperty
  def timestamp_human(self):
    result = ''
    if self.accuracy == 'year':
      result = self.timestamp.strftime('%Y')
    elif self.accuracy == 'month':
      result = self.timestamp.strftime('%B %Y')
    else:
      result = self.timestamp.strftime('%d %b %Y')

    if self.timestamp.hour > 0:
      result += self.timestamp.strftime(' @ %H:00')
    return result

  @ndb.ComputedProperty
  def timestamp_tax(self):
    result = ''
    if self.accuracy == 'year':
      result = self.timestamp.strftime('%Y')
    elif self.accuracy == 'month':
      result = self.timestamp.strftime('%m/%Y')
    else:
      result = self.timestamp.strftime('%m/%d/%Y')

    return result

  @classmethod
  def get_dbs(cls, **kwargs):
    return super(Event, cls).get_dbs(
        country_code=util.param('country_code'),
        **kwargs
      )

  FIELDS = {
      'accuracy': fields.String,
      'address': fields.String,
      'country': fields.String,
      'country_code': fields.String,
      'geo_pt': fields.GeoPt,
      'home': fields.Boolean,
      'layover': fields.Boolean,
      'notes': fields.String,
      'place': fields.String,
      'search': fields.String,
      'timestamp': fields.DateTime,
      'user_key': fields.Key,
    }

  FIELDS.update(model.Base.FIELDS)
