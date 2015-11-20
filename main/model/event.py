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

  @classmethod
  def get_dbs(cls, **kwargs):
    return super(Event, cls).get_dbs(
        country_code=util.param('country_code'),
        **kwargs
      )

  FIELDS = {
      'user_key': fields.Key,
      'search': fields.String,
      'address': fields.String,
      'place': fields.String,
      'country': fields.String,
      'country_code': fields.String,
      'geo_pt': fields.GeoPt,
      'layover': fields.Boolean,
      'timestamp': fields.DateTime,
      'accuracy': fields.String,
      'notes': fields.String,
    }

  FIELDS.update(model.Base.FIELDS)
