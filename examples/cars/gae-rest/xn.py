import os, re, sys, types
sys.path += [os.path.abspath(os.path.dirname(__file__))]
import glob, urllib2
import wsgiref.handlers
from google.appengine.ext import db
from google.appengine.ext import webapp
from xnquery import *

class XNExposedModel(db.Model):
  name = db.StringProperty()
  model_properties = db.StringListProperty()

def expose_model(name, cls):
  exposed_model = XNExposedModel()
  exposed_model.model_properties = cls.properties().keys()
  exposed_model.name = name
  exposed_model.put()

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
  if len(only) > 0:
    for model in only:
      for lf in loadedfiles:
        if model in dir(lf):
          obj = getattr(lf, model)
          if type(obj) == db.PropertiedClass:
            expose_model(model, obj)
  else:
    for lf in loadedfiles:
      for name in dir(lf):
        obj = getattr(lf, name)
        if type(obj) == db.PropertiedClass:
          expose_model(name, obj)

expose()

def retrieve_model_property_list(entity):
  q = db.GqlQuery("SELECT * FROM XNExposedModel WHERE name = :1", entity)
  return q[0].model_properties

class XNQueryHandler(webapp.RequestHandler):
  def get(self, format, version, query):
    xnquery = XNQueryParser(query, os.environ['QUERY_STRING'])
    self.response.headers['Content-Type'] = 'text/plain'
    gqlquery = GQLQueryBuilder(xnquery)
    objects = db.GqlQuery(str(gqlquery))
    for object in objects:
      self.response.out.write('$object[type=%s]: %s\n' % (xnquery.resources.content.selectors.type.rightside, repr(content)))
    self.response.out.write('[debug] Entity property list: %s.' % repr(retrieve_model_property_list(xnquery.resources.content.selectors.type.rightside)))

def main():
  application = webapp.WSGIApplication([('/xn/(.*)/(.*)/(.*)', XNQueryHandler)], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()