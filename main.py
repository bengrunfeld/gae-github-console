"""
Render the front end of the app
"""

import webapp2

from google.appengine.api import urlfetch

from basehandler import BaseHandler


class RenderApp(BaseHandler):
    """
    Check that the user is logged in, then render the front end of the app
    """
    
    def get(self):

        # Check that user is logged in. Send to auth if False
        if not self.session.get('logged_in'):
            self.redirect('/auth')

        # Render the app
        self.render('index')


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': ''  # use secret key
}

application = webapp2.WSGIApplication([
    ('/app', RenderApp),
], config=config, debug=True)
