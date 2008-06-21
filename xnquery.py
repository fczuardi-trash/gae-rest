__author__ = ('Jonas Galvez', 'jonas@codeazur.com.br', 'http://jonasgalvez.com.br')

import re
import unittest

class InvalidResource(Exception): pass
class InvalidSelectorOperator(Exception): pass

# Storage helper class comes from web.py, props to Aaron Swartz
class Storage(dict):
  def __getattr__(self, key):
    try: return self[key]
    except KeyError, k: raise AttributeError, k
  def __setattr__(self, key, value):
    self[key] = value
  def __delattr__(self, key):
    try: del self[key]
    except KeyError, k: raise AttributeError, k
  def __repr__(self):
    return '<Storage ' + dict.__repr__(self) + '>'

# TO-DO: add code to determine type (string, int etc)
class XNSelector(Storage):
  BASIC_OPERATORS = ('<>', '<=', '>=', '<', '>', '=')
  CONDITION = re.compile("""^[^=><]*(.*?)['"]*$""")
  LINE_STRIP_QUOTES = re.compile("""^['"]*(.*?)['"]*$""")
  def __init__(self, operator, leftside, rightside):
    self.operator = operator
    self.leftside = leftside
    quote_stripped = XNSelector.LINE_STRIP_QUOTES.match(rightside)
    if quote_stripped: self.rightside = quote_stripped.group(1)
    else: self.rightside = rightside
    self.rightside_raw = rightside
  @staticmethod
  def parse(fromstring):
    for op in XNSelector.BASIC_OPERATORS:
      operands = fromstring.split(op)
      if len(operands) > 1:
        return XNSelector(op, *map(str.strip, operands))
    raise InvalidSelectorOperator

class XNQueryParser:
  RESOURCE_AND_SELECTORS = re.compile("""([^(]+)(?:\((.*)\))?""")
  def __init__(self, resources, ordering):
    self.resources = Storage()
    self.ordering = Storage()
    self._parse_resources(resources)
    self._parse_selectors(self.ordering, ordering)
  def _parse_resources(self, resources):
    resources = resources.split('/')
    for resource in resources:
      m = XNQueryParser.RESOURCE_AND_SELECTORS.match(resource)
      if m:
        resource_name = m.group(1)
        self.resources[resource_name] = Storage()
        resource_obj = self.resources[resource_name]
        selectors = m.group(2)
        if selectors:
          resource_obj.selectors = Storage()
          self._parse_selectors(resource_obj.selectors, selectors)
  def _parse_selectors(self, obj, selectors):
    if selectors == None:
      return None
    for selector in selectors.split('&'):
      xnsel = XNSelector.parse(selector)
      if xnsel: obj[xnsel.leftside] = xnsel

class GQLQueryBuilder:
  KNOWN_RESOURCES = ('content',)
  def __init__(self, xnquery):
    self.resources = xnquery.resources
    self.ordering = xnquery.ordering
    self.gql_query = ['select']
    self.process_known_resources()
  def process_known_resources(self):
    for res in GQLQueryBuilder.KNOWN_RESOURCES:
      getattr(self, 'process_%s' % res)()
  def process_content(self):
    if 'content' in self.resources:
      content = self.resources['content']
      self.entity = content.selectors['type'].rightside
      self.gql_query += ['*', 'from', self.entity]
      if len(content.selectors.keys()) > 1:
        self.gql_query += ['where']
        for name, selector in content.selectors.items():
          if name == 'type': continue # TO-DO: make it so that you don't have to do this
          self.gql_query += [selector.leftside, selector.operator, selector.rightside_raw]
  def __str__(self):
    return '%s;' % ' '.join(self.gql_query)

class XNQueryTester(unittest.TestCase):
  queries = (
    ("profile(id='david')", None),
    ("content(type='User'&author='david')", None),
    ("content", "order=published@D"),
    ("content(type='Photo')", "order=my.viewCount@D&from=0&to=10"),
    ("content(type='Topic'&my.xg_forum_commentCount>1)", "order=my.xg_forum_commentCount@D&from=0&to=5")
  )
  def test_author_is_david(self):
    sample_query = self.queries[1]
    xnquery = XNQueryParser(sample_query[0], sample_query[1])
    assert xnquery.resources['content'].selectors['author'].rightside == 'david'
  def test_order_parsing(self):
    sample_query = self.queries[3]
    xnquery = XNQueryParser(sample_query[0], sample_query[1])
    assert xnquery.ordering['order'].rightside == 'my.viewCount@D'
  def test_gql_query_builder(self):
    sample_query = sample_query = self.queries[1]
    xnquery = XNQueryParser(sample_query[0], sample_query[1])
    gqlquery = GQLQueryBuilder(xnquery)
    assert str(gqlquery) == """select * from User where author = 'david';"""

if __name__ == '__main__':
  unittest.main()