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
  for name, dirs, files in os.walk(os.path.join(__file__, '..', '..')):
    pyfiles = glob.glob('%s/*.py' % name)
    for pyfile in pyfiles:
      pydir, pyfile = os.path.split(pyfile)
      pyfile = os.path.splitext(pyfile)[0]
      if pyfile in ('__init__', 'xn', 'xnquery'): continue
      sys.path += [pydir]
      loadedfiles.append(__import__(pyfile))
      sys.path.remove(pydir)
  if len(only) > 0:
    for model in only:
      if model in sandboxed_globals:
        expose_model(model, sandboxed_globals['model'])
  else:
    for lf in loadedfiles:
      for name in dir(lf):
        obj = getattr(lf, name)
        if type(obj) == type(db.PropertiedClass):
          expose_model(name, obj)

expose()

def retrieve_model_property_list(entity):
  q = db.GqlQuery("SELECT * FROM XNExposedModel WHERE name = 'Car'")#:1", entity)
  return q[0].model_properties

class XNQueryHandler(webapp.RequestHandler):
  def get(self, format, version, query):
    xnquery = XNQueryParser(query, os.environ['QUERY_STRING'])
    self.response.headers['Content-Type'] = 'text/plain'
    #self.response.out.write(repr(expose()))
    #return
    gqlquery = GQLQueryBuilder(xnquery)
    contents = db.GqlQuery(str(gqlquery))
    for content in contents:
      self.response.out.write('$content: %s\n' % repr(content))
    self.response.out.write(retrieve_model_property_list(xnquery.resources.content.selectors.type.rightside))

def main():
  application = webapp.WSGIApplication([('/xn/(.*)/(.*)/(.*)', XNQueryHandler)], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()