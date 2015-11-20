# coding: utf-8

from __future__ import absolute_import

import hashlib

from flask.ext.babel import lazy_gettext as _
from google.appengine.ext import ndb

from api import fields
import model
import util
import config


class User(model.Base):
  name = ndb.StringProperty(required=True, verbose_name=_('Name'))
  username = ndb.StringProperty(required=True, verbose_name=_('Username'))
  email = ndb.StringProperty(default='', verbose_name=_('Email'))
  locale = ndb.StringProperty(default='', verbose_name=_('Language'))
  auth_ids = ndb.StringProperty(repeated=True)
  active = ndb.BooleanProperty(default=True, verbose_name=_('Active'))
  admin = ndb.BooleanProperty(default=False, verbose_name=_('Admin'))
  permissions = ndb.StringProperty(repeated=True, verbose_name=_('Permissions'))
  verified = ndb.BooleanProperty(default=False, verbose_name=_('Verified'))
  token = ndb.StringProperty(default='')
  home = ndb.StringProperty(default='')
  is_public = ndb.BooleanProperty(default=False)
  password_hash = ndb.StringProperty(default='')

  def has_permission(self, perm):
    return self.admin or perm in self.permissions

  def avatar_url_size(self, size=None):
    return '//gravatar.com/avatar/%(hash)s?d=identicon&r=x%(size)s' % {
        'hash': hashlib.md5(
            (self.email or self.username).encode('utf-8')).hexdigest(),
        'size': '&s=%d' % size if size > 0 else '',
      }
  avatar_url = property(avatar_url_size)

  @classmethod
  def get_dbs(
      cls, admin=None, active=None, verified=None, permissions=None, **kwargs
    ):
    return super(User, cls).get_dbs(
        admin=admin or util.param('admin', bool),
        active=active or util.param('active', bool),
        verified=verified or util.param('verified', bool),
        permissions=permissions or util.param('permissions', list),
        **kwargs
      )

  @classmethod
  def is_username_available(cls, username, self_key=None):
    if self_key is None:
      return cls.get_by('username', username) is None
    user_keys, _ = util.get_keys(cls.query(), username=username, limit=2)
    return not user_keys or self_key in user_keys and not user_keys[1:]

  @classmethod
  def is_email_available(cls, email, self_key=None):
    if not config.CONFIG_DB.check_unique_email:
      return True
    user_keys, _ = util.get_keys(
        cls.query(), email=email, verified=True, limit=2,
      )
    return not user_keys or self_key in user_keys and not user_keys[1:]

  def get_event_dbs(self, order=None, **kwargs):
    return model.Event.get_dbs(
        user_key=self.key,
        order=order or util.param('order') or '-timestamp,accuracy,-created',
        **kwargs
      )

  FIELDS = {
      'active': fields.Boolean,
      'admin': fields.Boolean,
      'auth_ids': fields.List(fields.String),
      'avatar_url': fields.String,
      'email': fields.String,
      'locale': fields.String,
      'name': fields.String,
      'permissions': fields.List(fields.String),
      'username': fields.String,
      'verified': fields.Boolean,
    }

  FIELDS.update(model.Base.FIELDS)
