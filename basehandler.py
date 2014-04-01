"""
Provide the necessary setup to run the GAE application

The BaseHandler centralizes all the import statements so that
they only need to be declared in one place.

The Jinja2 environment is also set up here.

"""

import os

import jinja2
import json
import webapp2

from google.appengine.api import urlfetch
from webapp2_extras import sessions

TEMPLATE_DIR = 'templates'
TEMPLATE_SUFFIX = '.html'

GITHUB_API_URL = 'https://api.github.com'
ACCESS_TOKEN = '?access_token=' + os.environ.get('ACCESS_TOKEN')

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

    def query(self, url, payload='', method='GET'):
        """Queries Github and returns the result of the request"""

        # parse the url properly
        url = GITHUB_API_URL + url + ACCESS_TOKEN

        # if there is a payload, parse it
        if payload:
            data = json.dumps(payload)

        # Build the urlfetch based on the HTTP request specified
        if method in 'GET':
            result = urlfetch.fetch(url=url)

        if method in 'POST':
            result = urlfetch.fetch(url=url, payload=data,
                                    method=urlfetch.POST)

        if method in 'PUT':
            result = urlfetch.fetch(url=url, payload=data, method=urlfetch.PUT)

        if method in 'PATCH':
            result = urlfetch.fetch(url=url, payload=data,
                                    method=urlfetch.PATCH)

        # Convert the result to something useable, if it exists
        if result.content:
            response = json.loads(result.content)
        else:
            response = False

        return response

    def sort_results(self, results, attribute, attribute2=''):
        """Sorts the results returned from a request"""

        # Declare a dictionary to store the results
        response = []

        # Multiple conditions need to be set
        if attribute2:
            for result in results:
                if (attribute in result and result[attribute] and
                        attribute2 in result and result[attribute2]):
                    response.append(result[attribute])

            return response

        # Only a single condition needs to be set
        for result in results:
            if self.request.get(attribute):
                response.append(result[attribute])

        return response
