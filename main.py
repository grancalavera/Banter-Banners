#!/usr/bin/env python
import logging
import os
import random
from exceptions import Exception

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
from pyamf.remoting.gateway.google import WebAppGateway
import pyamf


WARNING_THRESHOLD = 15

def create_banner(**kwargs):
    """Creates a banner in the datastore"""
    
    team = Team.get_by_key_name(kwargs.get('team_name'))
    
    if not team.enabled:
        team.enabled = True
        team.put()
    
    Banner(
        copy = kwargs.get('copy'),
        team = team,
        author_id = kwargs.get('author_id')
    ).put()
    

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


def get_banner_for_team(team):
    """
    Serves a banner. Takes care of recording the banner impression and also
    of sending default placeholder content when there are no more banners
    """
    banner = get_random_banner_for_team(team)

    if banner:
        record_banner_impression(banner.key())

    return banner


def get_random_banner_for_team(team):
    """
    Returns a random bannner from the banners that still have impressions
    remaining.
    Returns None if there are no banners with impressions remaining
    """
    banners = team.banners.filter('impressions >', 0)
    count = banners.count()
    
    banner = None
    
    if count:
        banner = banners[random.randint(0, count -1)]
    
    return banner


def record_banner_impression(key):
    """
    Records (actually subtracts) a banner impression. Then adds a task to the
    default queue to update the queue status
    """
    banner = Banner.get(key)
    banner.impressions -= 1
    banner.put()
    # do this here, not in the queue
    # taskqueue.add(url = '/workers/update_queue_status', params = {'key' : key})
    update_queue_status_for_team(key)


def update_queue_status_for_team(key):
    """
    Based on a banner key, retrieves the appropriate team and updates its queue
    status
    """
    team = Banner.get(key).team
    if not team.enabled:
        return
    
    banners = team.banners
    impressions_remaining = 0
    for banner in banners: impressions_remaining += banner.impressions
    
    if impressions_remaining == 0:
        handle_queue_empty_for_team(team)
    elif impressions_remaining == WARNING_THRESHOLD:
        handle_threshold_reached_for_team(team)


def handle_threshold_reached_for_team(team):
    """
    Handles all operations to be performed when the queue of banners for a 
    particular team is about to be depleted
    """
    logging.info('The banner impressions for the %s team are running low.' %team.name)


def handle_queue_empty_for_team(team):
    """
    Handles all operations to be performed when all the banners have run our of
    impressions
    """
    logging.info('%s disabled' %team.name)
    team.enabled = False;
    team.put();
    
    logging.info('The banner impressions for the %s team are over.' %team.name)


"""
AMF services
"""

def amf_echo(data):
    """
    Echoes the data back to the client
    """
    return data


def amf_get_banner(team_name):
    """
    AMF proxy for the get_banner_for_team function
    """
    try:
        team = Team.get_by_key_name(team_name)
        banner = get_banner_for_team(team)
        return banner.copy
        
    except Exception:
        return 'Banter Banners!'
    

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
    def render(self, template_file, template_values):
        """
        Convenience method to render templates
        """
        template_values.update(get_default_template_values(self.request.path))
        path = os.path.join(os.path.dirname(__file__), 'templates/%s' %template_file)
        template_render = template.render(path, template_values)
        self.response.out.write(template_render)


class IndexHandler(MainHandler):
    def get(self):
        data = {}
        data['create_banner_url'] = '/create_banner'

        if (users.get_current_user()):
            data['banners'] = get_banners_for_current_user()

        self.render('index.html', data)


class BannerHandler(webapp.RequestHandler):
    def get(self):
        team_name = self.request.get('team')
        self.response.headers["Content-Type"] = 'text/plain'
        
        try:
            team = Team.get_by_key_name(team_name)
            banner = get_banner_for_team(team)
            self.response.out.write(banner.copy)
            
        except Exception:
            self.response.out.write('Banter Banners!')

class FlashBannerHandler(MainHandler):
    def get(self):
        self.render('flash_banner.html', {})


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
        create_banner(
            team_name = self.request.get('team'),
            copy = self.request.get('copy'),
            author_id = self.request.get('author')
        )


class UpdateQueueStatusWorker(webapp.RequestHandler):
    """
    A proxy to rout the banner queue updating to the appropriate function
    """
    def post(self):
        key = self.request.get('key')
        update_queue_status_for_team(key)


def main():
    debug = True
    
    logging.getLogger().setLevel(logging.DEBUG)
    
    amf_services = {
        'banter_banners.echo' : amf_echo,
        'banter_banners.getBanner' : amf_get_banner,
    }
    
    AMF_NAMESPACE = 'com.razorfish.banterbanners.models'
    pyamf.register_class(Banner, '%s.Banner' % AMF_NAMESPACE)
    pyamf.register_class(Team, '%s.Team' % AMF_NAMESPACE)
    
    amf_gateway = WebAppGateway(
        amf_services, 
        logger = logging,
        debug = debug
    )

    paths = [
        ('/amf', amf_gateway),
        ('/banner', BannerHandler),
        ('/create_banner', BannerFormHandler),
        ('/flash_banner', FlashBannerHandler),
        ('/workers/update_queue_status', UpdateQueueStatusWorker),
        ('/workers/create_banner', CreateBannerWorker),
        ('/', IndexHandler),
        ('/.*', MainHandler),
    ];

    application = webapp.WSGIApplication(paths, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
 