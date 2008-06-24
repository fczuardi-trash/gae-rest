import os, re, sys, types
sys.path += [os.path.abspath(os.path.dirname(__file__))]
import glob, urllib2
import urllib
import wsgiref.handlers
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from xnquery import *

def expose(only=[]):
  loadedfiles = []
  ignorelist = [os.path.splitext(os.path.split(f)[1])[0] for f in
                glob.glob(os.path.join(os.path.abspath(os.path.dirname(__file__)), '*.py'))]
  for name, dirs, files in os.walk(os.path.join(__file__, '..', '..')):
    pyfiles = glob.glob('%s/*.py' % name)
    for pyfile in pyfiles:
      pydir, pyfile = os.path.split(pyfile)
      pyfile = os.path.splitext(pyfile)[0]
      if pyfile in ignorelist: continue
      sys.path += [pydir]
      loadedfiles.append(__import__(pyfile))
      sys.path.remove(pydir)

expose()

def build_object_list(objects):
  output = []
  for object in objects:
    o = Storage({'properties': []})
    for prop in object.properties().keys():
      o.properties.append(Storage({'name': prop, 'value': getattr(object, prop)}))
    output.append(o)
  return output

def retrieve_model_property_list(entity):
  q = db.GqlQuery("SELECT * FROM XNExposedModel WHERE name = :1", entity)
  return q[0].model_properties

class XNQueryHandler(webapp.RequestHandler):
  def get(self, format, version, query):
    xnquery = XNQueryParser(query, os.environ['QUERY_STRING'])
    self.response.headers['Content-Type'] = 'text/plain'
    gqlquery = GQLQueryBuilder(xnquery)
    objects = db.GqlQuery(str(gqlquery))
    self.response.headers['Content-Type'] = 'application/atom+xml'
    path = os.path.join(os.path.dirname(__file__), "templates/atom.xml")
    self.response.out.write(template.render(path, {'objects': build_object_list(objects)}))

def main():
  application = webapp.WSGIApplication([('/xn/(.*)/(.*)/(.*)', XNQueryHandler)], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()