from __future__ import with_statement
import os, re, sys, types
sys.path += [os.path.split(os.path.abspath(__file__))[0]]
import glob, urllib2
import urllib
import wsgiref.handlers
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api.users import User
from xnquery import *
from xmlbuilder import *
import config

def expose(only=[]):
  rootdir = os.path.join(os.path.abspath(os.path.split(os.path.dirname(__file__))[0]))
  loadedfiles = []
  for model in config.models:
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
  def get(self, format, version, query):
    xnquery = XNQueryParser(query, os.environ['QUERY_STRING'])
    gqlquery = GQLQueryBuilder(xnquery)
    objects = db.GqlQuery(str(gqlquery))
    self.response.headers['Content-Type'] = 'application/atom+xml'
    kind = xnquery.resources.content.selectors.type.rightside
    atom = AtomBuilder(kind, objects)
    self.response.out.write(str(atom))

class AtomBuilder:
  FEED_NS = {
    'xmlns': 'http://www.w3.org/2005/Atom',
    'xmlns:xn': 'http://www.ning.com/atom/1.0'
  }
  def __init__(self, kind, objects):
    xml = builder(version='1.0', encoding='utf-8')
    with xml.feed(**self.FEED_NS):
      xml.title("GAE-REST Test Atom Feed")
      for object in objects:
        with xml.entry:
          for property in object.properties().keys():
            value = getattr(object, property)
            if (kind in config.creator) and property == config.creator[kind]:
              with xml.author:
                if type(value) == User:
                  xml.name(value.nickname())
                  xml.email(value.email())
                else:
                  xml.name(value)
            elif type(value) == list:
              xml["xn:%s" % property](' '.join(getattr(object, property)))
            else:
              xml["xn:%s" % property](getattr(object, property))
    self.xml = xml
  def __str__(self):
    return str(self.xml)

def main():
  application = webapp.WSGIApplication([('/xn/(.*)/(.*)/(.*)', XNQueryHandler)], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()