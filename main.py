#!/usr/bin/env python
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util


class MainHandler(webapp.RequestHandler):
    def get(self):
        logging.info('Hello world!')
        self.response.out.write('Hello world!')


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    
    paths = [
        ('/', MainHandler),
    ];
    
    application = webapp.WSGIApplication(paths, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
