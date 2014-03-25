"""
Provide the necessary setup to run the GAE application

The BaseHandler centralizes all the import statements so that
they only need to be declared in one place.

The Jinja2 environment is also set up here.

"""

import os

import jinja2
import webapp2

from webapp2_extras import sessions


TEMPLATE_DIR = 'templates'
TEMPLATE_SUFFIX = '.html'

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class BaseHandler(webapp2.RequestHandler):
    """BaseHandler provides a simple framework to ensure sessions are setup and
    to ease the displaying of HTML templates.
    """

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    def render(self, template_name, context):

        if not template_name.startswith(TEMPLATE_DIR):
            template_name = os.path.join(TEMPLATE_DIR, template_name)

        if not template_name.endswith(TEMPLATE_SUFFIX):
            template_name += TEMPLATE_SUFFIX

        template = JINJA_ENVIRONMENT.get_template(template_name)
        self.response.write(template.render(context))

