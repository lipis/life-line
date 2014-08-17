# coding: utf-8

from flask.ext import wtf
from flask.ext.babel import lazy_gettext as _
from google.appengine.api import app_identity
from google.appengine.ext import ndb
import flask

import auth
import config
import i18n
import model
import util

from main import app


class ConfigUpdateForm(i18n.Form):
  analytics_id = wtf.StringField('Tracking ID', filters=[util.strip_filter])
  announcement_html = wtf.TextAreaField('Announcement HTML', filters=[util.strip_filter])
  announcement_type = wtf.SelectField('Announcement Type', choices=[(t, t.title()) for t in model.Config.announcement_type._choices])
  bitbucket_key = wtf.StringField('Key', filters=[util.strip_filter])
  bitbucket_secret = wtf.StringField('Secret', filters=[util.strip_filter])
  brand_name = wtf.StringField('Brand Name', [wtf.validators.required()], filters=[util.strip_filter])
  dropbox_app_key = wtf.StringField('App Key', filters=[util.strip_filter])
  dropbox_app_secret = wtf.StringField('App Secret', filters=[util.strip_filter])
  facebook_app_id = wtf.StringField('App ID', filters=[util.strip_filter])
  facebook_app_secret = wtf.StringField('App Secret', filters=[util.strip_filter])
  feedback_email = wtf.StringField('Feedback Email', [wtf.validators.optional(), wtf.validators.email()], filters=[util.email_filter])
  flask_secret_key = wtf.StringField('Secret Key', [wtf.validators.optional()], filters=[util.strip_filter])
  locale = wtf.SelectField('Default Locale', choices=config.LOCALE_SORTED)
  github_client_id = wtf.StringField('Client ID', filters=[util.strip_filter])
  github_client_secret = wtf.StringField('Client Secret', filters=[util.strip_filter])
  instagram_client_id = wtf.StringField('Client ID', filters=[util.strip_filter])
  instagram_client_secret = wtf.StringField('Client Secret', filters=[util.strip_filter])
  linkedin_api_key = wtf.StringField('API Key', filters=[util.strip_filter])
  linkedin_secret_key = wtf.StringField('Secret Key', filters=[util.strip_filter])
  microsoft_client_id = wtf.StringField('Client ID', filters=[util.strip_filter])
  microsoft_client_secret = wtf.StringField('Client Secret', filters=[util.strip_filter])
  notify_on_new_user = wtf.BooleanField('Send an email notification when a user signs up')
  reddit_client_id = wtf.StringField('Key', filters=[util.strip_filter])
  reddit_client_secret = wtf.StringField('Secret', filters=[util.strip_filter])
  stackoverflow_client_id = wtf.StringField('Client Id', filters=[util.strip_filter])
  stackoverflow_client_secret = wtf.StringField('Client Secret', filters=[util.strip_filter])
  stackoverflow_key = wtf.StringField('Key', filters=[util.strip_filter])
  twitter_consumer_key = wtf.StringField('Consumer Key', filters=[util.strip_filter])
  twitter_consumer_secret = wtf.StringField('Consumer Secret', filters=[util.strip_filter])
  verify_email = wtf.BooleanField('Verify user emails')
  vk_app_id = wtf.StringField('App ID', filters=[util.strip_filter])
  vk_app_secret = wtf.StringField('App Secret', filters=[util.strip_filter])
  yahoo_consumer_key = wtf.StringField('Consumer Key', filters=[util.strip_filter])
  yahoo_consumer_secret = wtf.StringField('Consumer Secret', filters=[util.strip_filter])


@app.route('/_s/admin/config/', endpoint='admin_config_update_service')
@app.route('/admin/config/', methods=['GET', 'POST'])
@auth.admin_required
def admin_config_update():
  config_db = model.Config.get_master_db()
  form = ConfigUpdateForm(obj=config_db)
  if form.validate_on_submit():
    form.populate_obj(config_db)
    if not config_db.flask_secret_key:
      config_db.flask_secret_key = util.uuid()
    config_db.put()
    reload(config)
    app.config.update(CONFIG_DB=config_db)
    return flask.redirect(flask.url_for('welcome'))

  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_db(config_db)

  instances_url = None
  if config.PRODUCTION:
    instances_url = '%s?app_id=%s&version_id=%s' % (
        'https://appengine.google.com/instances',
        app_identity.get_application_id(),
        config.CURRENT_VERSION_ID,
      )

  return flask.render_template(
      'admin/config_update.html',
      title=_('Admin Config'),
      html_class='admin-config',
      form=form,
      config_db=config_db,
      instances_url=instances_url,
      has_json=True,
    )


@app.route('/_a/event/accuracy/')
@auth.admin_required
def update_user_tutor():
  event_dbs, event_cursor = util.get_dbs(
      model.Event.query(),
      limit=util.param('limit', int) or config.MAX_DB_LIMIT,
      order=util.param('order'),
      cursor=util.param('cursor'),
    )

  for event_db in event_dbs:
    event_db.accuracy = 'day'

  ndb.put_multi(event_dbs)
  return util.jsonify_model_dbs(event_dbs, event_cursor)


################################################################################
# User Stuff
################################################################################
@app.route('/admin/event/')
@auth.admin_required
def admin_event_list():
  event_dbs, next_cursor = util.get_dbs(
      model.Event.query(),
      limit=util.param('limit', int),
      cursor=util.param('cursor'),
      order=util.param('order') or 'user_key,-timestamp,accuracy,-created',
    )

  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_dbs(event_dbs, next_cursor)

  return flask.render_template(
      'admin/event_list.html',
      html_class='admin-event-list',
      title='Event List',
      event_dbs=event_dbs,
      next_url=util.generate_next_url(next_cursor),
    )
