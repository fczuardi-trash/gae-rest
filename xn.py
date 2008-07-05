from __future__ import with_statement
import os, re, sys, types
sys.path += [os.path.split(os.path.abspath(__file__))[0]]
import glob, urllib2
import urllib
import wsgiref.handlers
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from xnquery import *
from xmlbuilder import *
from models import *

def expose(only=[]):
  rootdir = os.path.join(os.path.abspath(os.path.split(os.path.dirname(__file__))[0]))
  loadedfiles = []
  for model in models:
    pydir, pyfile = os.path.split(model)
    pydir = os.path.abspath(os.path.join(rootdir, pydir))
    sys.path += [pydir]
    pyfile = os.path.splitext(pyfile)[0]
    loadedfiles.append(pyfile)
    __import__(pyfile)
    sys.path.remove(pydir)
  return loadedfiles

loadedfiles = expose()

def retrieve_model_property_list(entity):
  q = db.GqlQuery("SELECT * FROM XNExposedModel WHERE name = :1", entity)
  return q[0].model_properties

class XNQueryHandler(webapp.RequestHandler):
  FEED_NS = {
    'xmlns': 'http://www.w3.org/2005/Atom',
    'xmlns:xn': 'http://www.ning.com/atom/1.0'
  }
  def get(self, format, version, query):
    xnquery = XNQueryParser(query, os.environ['QUERY_STRING'])
    gqlquery = GQLQueryBuilder(xnquery)
    objects = db.GqlQuery(str(gqlquery))
    self.response.headers['Content-Type'] = 'application/atom+xml'
    xml = builder(version='1.0', encoding='utf-8')
    with xml.feed(**XNQueryHandler.FEED_NS):
      xml.title("GAE-REST Test Atom Feed")
      for object in objects:
        with xml.entry:
          for property in object.properties().keys():
            value = getattr(object, property)
            if type(value) == list:
              xml["xn:%s" % property](' '.join(getattr(object, property)))
            else:
              xml["xn:%s" % property](getattr(object, property))
    
    self.response.out.write(str(xml))

def main():
  application = webapp.WSGIApplication([('/xn/(.*)/(.*)/(.*)', XNQueryHandler)], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()