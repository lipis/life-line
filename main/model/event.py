# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb

import model


class Event(model.Base):
  user_key = ndb.KeyProperty(kind=model.User, required=True)
  search = ndb.StringProperty()
  address = ndb.StringProperty(required=True)
  place = ndb.StringProperty(required=True)
  country = ndb.StringProperty(required=True)
  country_code = ndb.StringProperty(default='')
  geo_pt = ndb.GeoPtProperty()
  layover = ndb.BooleanProperty(default=False)
  timestamp = ndb.DateTimeProperty()
  accuracy = ndb.StringProperty(default='year')
  notes = ndb.StringProperty()

  _PROPERTIES = model.Base._PROPERTIES.union({
      'search',
      'address',
      'place',
      'country',
      'country_code',
      'geo_pt',
      'layover',
      'timestamp',
      'accuracy',
      'notes',
    })
