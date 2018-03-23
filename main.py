from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
import webapp2
import json
import os
import urllib
import random
import string
import sys

CLIENT_ID = '698911262591-h26odkjcc3gb4pvtuhju2mu2nr1m5q7i.apps.googleusercontent.com'
SECRET = 'K4wEgcTOl22vlqdUX9pyKfXh'
REDIRECT = 'https://assignment3-496.appspot.com/oauth'
#random string from: https://pythontips.com/2013/07/28/generating-a-random-string/
STATE_STRING = ''.join([random.choice(string.ascii_letters + string.digits) for i in xrange(32)])

class MainPage(webapp2.RequestHandler):
    def get(self):
        siteUrl = 'https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id='
        siteUrl = siteUrl + CLIENT_ID
        siteUrl = siteUrl + '&redirect_uri=' + REDIRECT
        siteUrl = siteUrl + '&scope=email&state=' + STATE_STRING
        #self.response.write(siteUrl)

#using the template to get the url on the site from http://webapp2.readthedocs.io/en/latest/tutorials/gettingstarted/templates.html
        template_values = {
            'url': siteUrl,
            'url_linktext': 'Click This',
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.write(template.render(path, template_values))

class OauthHandler(webapp2.RequestHandler):
    def get(self):
        gotCode = self.request.GET['code']
        ourState = STATE_STRING
        theirState = self.request.GET['state']
        #confirm the state is the same
        if(ourState != theirState):
            sys.exit("We have the wrong state")
        #else:
        #    self.response.write("So far so good.")
        #using https://stackoverflow.com/questions/19102927/how-to-make-a-post-request-in-python-and-webapp2 to help
        post = {
            'code': gotCode,
            'client_secret': SECRET,
            'client_id': CLIENT_ID,
            'redirect_uri': REDIRECT,
            'grant_type': 'authorization_code'
        }
        load = urllib.urlencode(post)
        #using https://cloud.google.com/appengine/docs/standard/python/issue-requests to help
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        #url gotten from assignment lectures
        response = urlfetch.fetch(
            url = "https://www.googleapis.com/oauth2/v4/token",
            payload = load,
            method = urlfetch.POST,
            headers = headers
        )
        #self.response.write(response.content)
        #move to json to get at the token
        postResult = json.loads(response.content)
        token = postResult['access_token']
        #header and url info from lecture video
        header = {'Authorization': 'Bearer ' + token}
        newResponse = urlfetch.fetch(
            url = "https://www.googleapis.com/plus/v1/people/me",
            method = urlfetch.GET,
            headers = header
        )
        #self.response.write(newResponse.content)
        newResult = json.loads(newResponse.content)
        #so now we should have user information
        #need to string the url for it to work
        firstName = newResult['name']['givenName']
        lastName = newResult['name']['familyName']
        plusUrl = str(newResult['url'])
        #need to template for the next page to get the info back to them.
        template_values = {
            'first': firstName,
            'last': lastName,
            'link': plusUrl,
            'link_text': "Login to Google Plus",
            'state': ourState,
        }

        path = os.path.join(os.path.dirname(__file__), 'oauth.html')
        self.response.write(template.render(path, template_values))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/oauth', OauthHandler),
], debug=True)
