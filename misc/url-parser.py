"""Test script with parsing functions

This script can run on a regular python console, it is just a set of 
helper functions to extract resources, selectors and operators from urls
according to the rules described in 
http://developer.ning.com/notes/REST_API_Request_URL_Syntax

The idea is to use this in the main project as it matures.
"""

import urllib2
import re

# some possible urls
urls = (
    "http://networkcreators.ning.com/xn/atom/1.0",
    "http://networkcreators.ning.com/xn/atom/1.0/content()",
    "http://developer.ning.com/xn/atom/1.0/content?order=published@D",
    "http://networkcreators.ning.com/xn/atom/1.0/content(type='User'&author='david')",
    "http://brooklynartproject.ning.com/xn/atom/1.0/content(type='Photo')?order=my.viewCount@D&from=0&to=10",
    "http://networkcreators.ning.com/xn/atom/1.0/content(type='Topic'&my.xg_forum_commentCount>1)?order=my.xg_forum_commentCount@D&from=0&to=5",
    "http://jetsetshow.ning.com/xn/atom/1.0/content(type='Topic')?order=published@A&from=0&to=5",
    "http://developer.ning.com/xn/atom/1.0/content/rollup(field='type')",
    "http://networkcreators.ning.com/xn/atom/1.0/profile(id='david')",
    "http://brooklynartproject.ning.com/xn/atom/1.0/tag(value='brooklynbattle')/content(type='Photo')?order=my.ratingCount@D&from=0&to=10",
)

def param_parser(params):
    # TODO: handle operators other than = (>, < etc)
    if params is None or params == '': return []
    # hash = dict(param.split('=') for param in params.split('&'))
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

for url in urls:
    path = '?'.join(urllib2.urlparse.urlsplit(url)[2:4]) # /xn/atom/1.0 ...
    query = re.findall('atom/1\.0/(.*)', path) # content(type='Photo') ...
    if len(query) > 0:
        print repr(query_parser(query[0]))
    else :
        print '--'