#!/usr/bin/env python
import logging
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext.webapp import template # keep this import first
from django import forms

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.db import djangoforms
from google.appengine.ext.webapp import util

def get_default_template_values(dest_url=None): #redirect to current page
    """
    Returns default values used across templates
    """
    values = {}
    values['user'] = users.get_current_user()
    values['login_url'] = users.create_login_url(dest_url or '/')
    values['logout_url'] = users.create_logout_url(dest_url or '/')
    
    return values

def serve_banner():
    """
    Serves a banner. Takes care of recording the banner impression and also 
    of sending placeholder content when there are no more banners
    """
    pass

def get_random_banner():
    
    """
    Returns a random bannner from the banners that still have impressions 
    remaining.
    Returns None if there are no banners with impressions remaining
    """
    pass

def handle_queue_empty():
    """
    Handles all operations to be performed when all the banners have run our of
    impressions
    """
    pass

def record_banner_impression(banner):
    """
    Records (actually subtracts) a banner impression
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
    author = db.UserProperty(required=True)
    team = db.ReferenceProperty(Team, required=True, collection_name='banners')


class CreateBannerForm(forms.Form):
    """
    A Simple form to create a Banner
    """

    TEAM_CHOICES = [('', 'Select One')]
    TEAM_CHOICES.extend([(team.name, team.name) for team in Team.all()])
    
    copy = forms.CharField(max_length = 140, label='Banter')
    team = forms.ChoiceField(choices = TEAM_CHOICES)
    
    
class MainHandler(webapp.RequestHandler):
    def get(self):
        self.render('index.html', {'create_banner_url' : '/create_banner'})
    
    def render(self, template_file, template_values):
        """
        Convenience method to render templates
        """
        template_values.update(get_default_template_values(self.request.path))
        path = os.path.join(os.path.dirname(__file__), 'templates/%s' %template_file)
        self.response.out.write(template.render(path, template_values))


class BannerFormHandler(MainHandler):
    """Creates a new Banner model in the datastore"""
    
    def render_form(self, render_with_errors = False):
        data = {
            'form' : CreateBannerForm(),
            'form_action' : '/create_banner',
            'form_method' : 'post'
        }

        if render_with_errors:
            data['error_message'] = 'Did you write some banter? Did you chose a team to banter?'

        self.render('banner_form.html', data)
    
    def get(self):
        self.render_form()

    def post(self):
        form = CreateBannerForm(self.request)
        
        if form.is_valid():
            pass
        else:
            self.render_form(True)


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    
    paths = [
        ('/', MainHandler),
        ('/create_banner', BannerFormHandler),
    ];
    
    application = webapp.WSGIApplication(paths, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
