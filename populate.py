#!/usr/bin/env python
import logging
import os

# django setup
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext.webapp import template
# end django setup

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from main import Team, Banner


class PopulateHandler(webapp.RequestHandler):
    def get(self):
        
        resultlog = []
        
        for team in Team.all():
            team.delete()

        for banner in Banner.all():
            banner.delete()

        teams = [
            'Arsenal',
            'Aston Villa',
            'Birmingham City',
            'Blackburn Rovers',
            'Blackpool',
            'Bolton Wanderers',
            'Chelsea',
            'Everton',
            'Fulham',
            'Liverpool',
            'Manchester City',
            'Manchester United',
            'Newcastle United',
            'Stoke City',
            'Sunderland',
            'Tottenham Hotspur',
            'West Bromwich Albion',
            'West Ham United',
            'Wigan Athletic',
            'Wolverhampton Wanderers',
        ]

        for team in teams:
            t = Team(name=team, key_name=team, enabled=True)
            t.put()
            resultlog.append('Team with name \"%s\" created.' %t.name)


        random_banter = [
            '%s fans should better find a new team.',
            'I can\'t understand how %s call themselves a team.',
            'A footbal team? I thought you said %s.',
        ]

        resultlog.append('')
        
        impressions = int(self.request.get('impressions', default_value=2000))
        
        for team in teams:
            for banter in random_banter:
                b = Banner(
                    copy = banter %team,
                    team = Team.get_by_key_name(team),
                    author_id = 'leoncoto',
                    impressions = impressions
                )
                b.put()
                resultlog.append('New banter banner')
                resultlog.append('Banter: %s' %b.copy)
                resultlog.append('Sent to: %s' %b.team.name)
                resultlog.append('Impressions left: %i' %b.impressions)
                resultlog.append('')
            resultlog.append('')   

        template_values = {'resultlog' : resultlog }
        path = os.path.join(os.path.dirname(__file__), 'templates/pupulate.html')
        template_render = template.render(path, template_values)
        self.response.out.write(template_render)        
        
        
def main():
    debug = True
    logging.getLogger().setLevel(logging.DEBUG)
    
    paths = [
        ('/populate', PopulateHandler),
    ];

    application = webapp.WSGIApplication(paths, debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()