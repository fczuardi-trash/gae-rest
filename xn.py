from __future__ import with_statement
from datetime import datetime
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

expose()

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
  HANDLERS = {
    'title': lambda value: value,
    'content': lambda value: value.replace('<','&lt;'),
    'summary': lambda value: value.replace('<','&lt;'),
    'published': lambda value: '%sZ' % value.isoformat(),
    'updated': lambda value: '%sZ' % value.isoformat(),
    'author': 'process_author'
  }
  def __init__(self, kind, objects):
    xml = builder(version='1.0', encoding='utf-8')
    self.xml = xml
    self.kind = kind
    with xml.feed(**self.FEED_NS):
      xml.title("GAE-REST Test Atom Feed")
      for object in objects:
        with xml.entry:
          properties = object.properties()
          self.process_known_elements(object, properties)
          for property in properties:
            value = getattr(object, property)
            if type(value) == list:
              xml["xn:%s" % property](' '.join(value))
            else:
              xml["xn:%s" % property](str(value).replace('<','&lt;'))
    self.xml = xml
  def process_author(self, value):
    with self.xml.author:
      if type(value) == User:
        self.xml.name(value.nickname())
        self.xml.email(value.email())
      else:
        self.xml.name(value)
  def process_known_elements(self, object, properties):
    used_properties = {}
    for element in AtomBuilder.HANDLERS.keys():
      m_element = getattr(config, element).get(self.kind, None)
      if m_element != None:
        if type(AtomBuilder.HANDLERS[element]) != str:
          self.xml[element](AtomBuilder.HANDLERS[element](getattr(object, m_element)))
        else:
          getattr(self, AtomBuilder.HANDLERS[element])(getattr(object, m_element))
        used_properties[m_element] = True
    for property_name in used_properties.keys():
      del properties[property_name]
  def __str__(self):
    return str(self.xml)

def main():
  application = webapp.WSGIApplication([('/xn/(.*)/(.*)/(.*)', XNQueryHandler)], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()