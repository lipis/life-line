# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb

import config
import model
import util


class Config(model.Base):
  analytics_id = ndb.StringProperty(default='')
  announcement_html = ndb.TextProperty(default='')
  announcement_type = ndb.StringProperty(default='info', choices=[
      'info', 'warning', 'success', 'danger',
    ])
  bitbucket_key = ndb.StringProperty(default='')
  bitbucket_secret = ndb.StringProperty(default='')
  brand_name = ndb.StringProperty(default=config.APPLICATION_ID)
  dropbox_app_key = ndb.StringProperty(default='')
  dropbox_app_secret = ndb.StringProperty(default='')
  facebook_app_id = ndb.StringProperty(default='')
  facebook_app_secret = ndb.StringProperty(default='')
  feedback_email = ndb.StringProperty(default='')
  flask_secret_key = ndb.StringProperty(default=util.uuid())
  github_client_id = ndb.StringProperty(default='')
  github_client_secret = ndb.StringProperty(default='')
  instagram_client_id = ndb.StringProperty(default='')
  instagram_client_secret = ndb.StringProperty(default='')
  linkedin_api_key = ndb.StringProperty(default='')
  linkedin_secret_key = ndb.StringProperty(default='')
  locale = ndb.StringProperty(default='en')
  microsoft_client_id = ndb.StringProperty(default='')
  microsoft_client_secret = ndb.StringProperty(default='')
  notify_on_new_user = ndb.BooleanProperty(default=True)
  reddit_client_id = ndb.StringProperty(default='')
  reddit_client_secret = ndb.StringProperty(default='')
  stackoverflow_client_id = ndb.StringProperty(default='')
  stackoverflow_client_secret = ndb.StringProperty(default='')
  stackoverflow_key = ndb.StringProperty(default='')
  twitter_consumer_key = ndb.StringProperty(default='')
  twitter_consumer_secret = ndb.StringProperty(default='')
  verify_email = ndb.BooleanProperty(default=True)
  vk_app_id = ndb.StringProperty(default='')
  vk_app_secret = ndb.StringProperty(default='')
  yahoo_consumer_key = ndb.StringProperty(default='')
  yahoo_consumer_secret = ndb.StringProperty(default='')

  @property
  def has_bitbucket(self):
    return bool(self.bitbucket_key and self.bitbucket_secret)

  @property
  def has_dropbox(self):
    return bool(self.dropbox_app_key and self.dropbox_app_secret)

  @property
  def has_facebook(self):
    return bool(self.facebook_app_id and self.facebook_app_secret)

  @property
  def has_github(self):
    return bool(self.github_client_id and self.github_client_secret)

  @property
  def has_instagram(self):
    return bool(self.instagram_client_id and self.instagram_client_secret)

  @property
  def has_linkedin(self):
    return bool(self.linkedin_api_key and self.linkedin_secret_key)

  @property
  def has_reddit(self):
    return bool(self.reddit_client_id and self.reddit_client_secret)

  @property
  def has_stackoverflow(self):
    return bool(self.stackoverflow_client_id and self.stackoverflow_client_secret and self.stackoverflow_key)

  @property
  def has_twitter(self):
    return bool(self.twitter_consumer_key and self.twitter_consumer_secret)

  @property
  def has_vk(self):
    return bool(self.vk_app_id and self.vk_app_secret)

  @property
  def has_microsoft(self):
    return bool(self.microsoft_client_id and self.microsoft_client_secret)

  @property
  def has_yahoo(self):
    return bool(self.yahoo_consumer_key and self.yahoo_consumer_secret)

  _PROPERTIES = model.Base._PROPERTIES.union({
      'analytics_id',
      'announcement_html',
      'announcement_type',
      'bitbucket_key',
      'bitbucket_secret',
      'brand_name',
      'dropbox_app_key',
      'dropbox_app_secret',
      'facebook_app_id',
      'facebook_app_secret',
      'feedback_email',
      'flask_secret_key',
      'github_client_id',
      'github_client_secret',
      'instagram_client_id',
      'instagram_client_secret',
      'linkedin_api_key',
      'linkedin_secret_key',
      'locale',
      'microsoft_client_id',
      'microsoft_client_secret',
      'notify_on_new_user',
      'reddit_client_id',
      'reddit_client_secret',
      'stackoverflow_client_id',
      'stackoverflow_client_secret',
      'stackoverflow_key',
      'twitter_consumer_key',
      'twitter_consumer_secret',
      'verify_email',
      'vk_app_id',
      'vk_app_secret',
      'yahoo_consumer_key',
      'yahoo_consumer_secret',
    })

  @classmethod
  def get_master_db(cls):
    return cls.get_or_insert('master')
