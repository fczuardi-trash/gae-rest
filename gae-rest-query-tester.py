import os
import re
import urllib2
import wsgiref.handlers
from google.appengine.ext import webapp

class GaeRestQueryTester(webapp.RequestHandler):
    
    def get(self, format, version, query):
        elems, params = query_parser('?'.join([query, os.environ['QUERY_STRING']]))
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('$format: %s\n' % format)
        self.response.out.write('$version: %s\n' % version)
        self.response.out.write('$elems: %s\n' % repr(elems))
        self.response.out.write('$params: %s\n' % repr(params))

def param_parser(params):
    if params is None or params == '': return []
    return params.split('&')

def element_parser(elements):
    hash = {}
    elements = elements.split('/')
    for element in elements:
        name, params = re.findall('([^(]*)(?:\((.*)\))?', element)[0]
        hash[name] = param_parser(params)
    return hash

def query_parser(query):
    query = urllib2.unquote(query)
    elements, params = urllib2.splitquery(query) # foo?bar=1 becomes ('foo', 'bar=1')
    return element_parser(elements), param_parser(params)

def main():
    application = webapp.WSGIApplication([('/xn/(.*)/(.*)/(.*)', GaeRestQueryTester)], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()