import os
import re
import urllib2
import wsgiref.handlers
from google.appengine.ext import db
from google.appengine.ext import webapp

# testing first change via git

class GaeRestQueryTester(webapp.RequestHandler):

    def get(self, format, version, query):
        elems, params = query_parser('?'.join([query, os.environ['QUERY_STRING']]))
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('$format: %s\n' % format)
        self.response.out.write('$version: %s\n' % version)
        self.response.out.write('$elems: %s\n' % repr(elems))
        self.response.out.write('$params: %s\n' % repr(params))

class GAERestQuery(webapp.RequestHandler):
    # TODO - it looks like you need to have the Entity Model declared in
    # order to query, otherwise the system raises a KindError
    # one possible and hackish way to workaround this limitation would
    # be to crawl the whole source code and check all the files that has
    # class Something(db.Expando) or class Something(db.Model) and them
    # import all of them here before making the query
    #
    # Worst case scenario we ask for the app owner to import the
    # necessary models here or ina a text file as part of the
    # installation instructions. I do realize this is lame, but probably
    # what we can do for now :(
    #
    # Here is a thread to keep track of:
    # http://groups.google.com/group/google-appengine/browse_thread/thread/e6fa946c7a713235
    def get(self, format, version, query):
        elems, params = query_parser('?'.join([query, os.environ['QUERY_STRING']]))
        if elems['content']:
            self.response.headers['Content-Type'] = 'text/plain'
            contentquery = elems['content'][0]
            contenttype = re.findall('type(s*)=(s*)\'([^\']*)', contentquery)[0][2]
            if contenttype:
                gql = "SELECT * FROM " + contenttype
                contents = db.GqlQuery(gql)
                for content in contents:
                    self.response.out.write('$content: %s\n' % repr(content))


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
    application = webapp.WSGIApplication([('/xn/(.*)/(.*)/(.*)', GAERestQuery)], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()