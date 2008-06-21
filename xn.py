import os
import re
import urllib2
import wsgiref.handlers
from google.appengine.ext import db
from google.appengine.ext import webapp
from xnquery import *

class XNQueryHandler(webapp.RequestHandler):
  def get(self, format, version, query):
    xnquery = XNQueryParser(query, os.environ['QUERY_STRING'])
    gqlquery = GQLQueryBuilder(xnquery)
    contents = db.GqlQuery(str(gqlquery))
    for content in contents:
      self.response.out.write('$content: %s\n' % repr(content))

def main():
  application = webapp.WSGIApplication([('/xn/(.*)/(.*)/(.*)', XNQueryHandler)], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()