#!/usr/bin/env python
import logging
import os
import random

# django setup
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext.webapp import template
# end django setup

from django import forms
from google.appengine.api import taskqueue
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.db import djangoforms
from google.appengine.ext.webapp import util


def get_banners_for_current_user():
    banners = Banner.all()
    banners.order('-created')
    return banners.filter('author_id = ', users.get_current_user().nickname())


def get_default_template_values(dest_url=None):
    """
    Returns default values used across templates
    """
    values = {}
    values['user'] = users.get_current_user()
    values['login_url'] = users.create_login_url(dest_url or '/')
    values['logout_url'] = users.create_logout_url(dest_url or '/')
    return values


def serve_banner_for_team(team):
    """
    Serves a banner. Takes care of recording the banner impression and also
    of sending default placeholder content when there are no more banners
    """
    banner = get_random_banner_for_team(team)

    if banner is not None:
        record_banner_impression(banner)

    return banner


def get_random_banner_for_team(team):
    """
    Returns a random bannner from the banners that still have impressions
    remaining.
    Returns None if there are no banners with impressions remaining
    """
    logging.info('Will send you a banner from the %s team' %team.name)
    banners = team.banners.filter('impressions >', 0)
    count = banners.count()
    
    banner = None
    
    if count:
        banner = banners[random.randint(0, count -1)]
    
    return banner


def handle_queue_empty_for_team(team):
    """
    Handles all operations to be performed when all the banners have run our of
    impressions
    """
    pass


def update_queue_status_for_team(team):
    """
    Gets the number of banners left in the queue and performs different actions
    based on this number
    """
    pass


def record_banner_impression(banner):
    """
    Records (actually subtracts) a banner impression. If the banners has no
    impressions remaining after recording an impression, this method will
    notify the banner queue is empty
    """
    pass


class Team(db.Model):
    """
    BanterTarget representation
    """
    name = db.StringProperty(required=True)
    enabled = db.BooleanProperty(default=True)


class Banner(db.Model):
    """
    Banner representation
    """
    impressions = db.IntegerProperty(required=True, default=2000)
    copy = db.StringProperty(required=True)
    author_id = db.StringProperty(required=True)
    team = db.ReferenceProperty(Team, required=True, collection_name='banners')
    created = db.DateTimeProperty(auto_now_add = True)


class BannerForm(forms.Form):
    """
    A Simple form to create a Banner
    """

    TEAM_CHOICES = [('', 'Select One')]
    TEAM_CHOICES.extend([(team.name, team.name) for team in Team.all()])

    team = forms.ChoiceField(choices = TEAM_CHOICES)
    copy = forms.CharField(max_length = 140, label='Banter', widget=forms.Textarea)


class MainHandler(webapp.RequestHandler):
    def get(self):
        data = {}
        data['create_banner_url'] = '/create_banner'

        if (users.get_current_user()):
            data['banners'] = get_banners_for_current_user()

        self.render('index.html', data)

    def render(self, template_file, template_values):
        """
        Convenience method to render templates
        """
        template_values.update(get_default_template_values(self.request.path))
        path = os.path.join(os.path.dirname(__file__), 'templates/%s' %template_file)
        self.response.out.write(template.render(path, template_values))


class BannerFormHandler(MainHandler):
    """
    Creates a new Banner model in the datastore
    """

    def render_form(self, form):
        data = {
            'form' : form,
            'form_action' : '/create_banner',
            'form_method' : 'post'
        }

        self.render('banner_form.html', data)

    def create_banner_from_form(self, form):
        
        banner_data = {
            'copy' : form.cleaned_data['copy'],
            'team' : form.cleaned_data['team'],
            'author' : users.get_current_user().nickname()
        }
        
        taskqueue.add(
            url = '/workers/create_banner', 
            params = banner_data
        )
        
        self.redirect('/')

    def get(self):
        self.render_form(BannerForm())

    def post(self):
        form = BannerForm(self.request)

        if form.is_valid():
            self.create_banner_from_form(form)
        else:
            self.render_form(form)


class CreateBannerWorker(webapp.RequestHandler):
    """
    Creates a new banner in the datastore
    """
    
    def post(self):
        team = Team.get_by_key_name(self.request.get('team'))
        
        Banner(
            copy = self.request.get('copy'),
            team = team,
            author_id = self.request.get('author')
        ).put()


class RecordImpressionWorker(webapp.RequestHandler):
    """
    Records 1 banner impression
    """
    
    def post(self):
        pass


def main():
    logging.getLogger().setLevel(logging.DEBUG)

    paths = [
        ('/', MainHandler),
        ('/create_banner', BannerFormHandler),
        ('/workers/record_impression', RecordImpressionWorker),
        ('/workers/create_banner', CreateBannerWorker)
    ];

    application = webapp.WSGIApplication(paths, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
