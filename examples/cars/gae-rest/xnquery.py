__author__ = ('Jonas Galvez', 'jonas@codeazur.com.br', 'http://jonasgalvez.com.br')

import re
import urllib2
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
  SPECIAL_SELECTORS = {'order': 'XNOrder'}
  BASIC_OPERATORS = ('<>', '<=', '>=', '<', '>', '=')
  CONDITION = re.compile("""^[^=><]*(.*?)['"]*$""")
  LINE_STRIP_QUOTES = re.compile("""^['"]*(.*?)['"]*$""")
  FIELD = re.compile("""^[A-Za-z][_.A-Z-a-z\d]+""")
  def __init__(self, operator, leftside, rightside):
    self.operator = operator
    self.leftside = leftside
    quote_stripped = XNSelector.LINE_STRIP_QUOTES.match(rightside)
    if quote_stripped: self.rightside = quote_stripped.group(1)
    else: self.rightside = rightside
    self.rightside_raw = rightside
    self.parse_right_side()
  def parse_right_side(self):
    is_field = XNSelector.FIELD.match(self.rightside_raw)
    if is_field:
      self.field = is_field.group()
      self.field = re.sub('^my\.', '', self.field)
  @staticmethod
  def parse(fromstring):
    for op in XNSelector.BASIC_OPERATORS:
      operands = fromstring.split(op)
      if len(operands) > 1:
        for field, selector in XNSelector.SPECIAL_SELECTORS.items():
          if operands[0].strip() == field:
            return globals()[selector](op, *map(str.strip, operands))
        return XNSelector(op, *map(str.strip, operands))
    return fromstring

class XNOrder(XNSelector):
  def __init__(self, *args, **kargs):
    XNSelector.__init__(self, *args, **kargs)
    order_raw = self.rightside.split('@')
    if len(order_raw) > 1:
      field, order = order_raw
      self.order = {'A': 'ASC', 'D': 'DESC'}[order]
    else:
      self.order = 'ASC'

class XNQueryParser:
  RESOURCE_AND_SELECTORS = re.compile("""([^(]+)(?:\((.*)\))?""")
  def __init__(self, resources, ordering):
    self.resources = Storage()
    self.ordering = Storage()
    self._parse_resources(urllib2.unquote(urllib2.unquote(resources))) # bizarre, figure out why
    self._parse_selectors(self.ordering, urllib2.unquote(ordering or ''))
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
    self.gql_query = ['SELECT']
    self.process_known_resources()
    self.process_ordering_conditions()
  def process_known_resources(self):
    for res in GQLQueryBuilder.KNOWN_RESOURCES:
      self.__dict__[res] = None
      getattr(self, 'process_%s' % res)()
  def process_content(self):
    if 'content' in self.resources:
      self.content = self.resources['content']
      self.entity = self.content.selectors['type'].rightside
      self.gql_query += ['*', 'FROM', self.entity]
      if len(self.content.selectors.keys()) > 1:
        self.gql_query += ['WHERE']
        for name, selector in self.content.selectors.items():
          if name == 'type': continue # TO-DO: make it so that you don't have to do this
          self.gql_query += [selector.leftside, selector.operator, selector.rightside_raw]
  def process_ordering_conditions(self):
    if self.content != None: # TO-DO: from, to
      order = self.ordering.get('order', None)
      if order != None:
        self.gql_query += ['ORDER BY', order.field, order.order]
  def __str__(self):
    return ' '.join(self.gql_query)

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
    assert xnquery.ordering['order'].field == 'viewCount'
    assert xnquery.ordering['order'].order == 'DESC'
  def test_simple_gql_query(self):
    sample_query = self.queries[1]
    xnquery = XNQueryParser(sample_query[0], sample_query[1])
    gqlquery = GQLQueryBuilder(xnquery)
    assert str(gqlquery) == """SELECT * FROM User WHERE author = 'david'"""
  def test_gql_query_with_order(self):
    sample_query = self.queries[3]
    xnquery = XNQueryParser(sample_query[0], sample_query[1])
    gqlquery = GQLQueryBuilder(xnquery)
    assert str(gqlquery) == """SELECT * FROM Photo ORDER BY viewCount DESC"""

if __name__ == '__main__':
  unittest.main()
  # helpful for debugging
  # sample_query = ("content(type='Photo')", "order=my.viewCount@D&from=0&to=10")
  # xnquery = XNQueryParser(sample_query[0], sample_query[1])
  # gqlquery = GQLQueryBuilder(xnquery)
  # print str(gqlquery)