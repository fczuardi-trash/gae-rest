__author__ = ('Jonas Galvez', 'jonas@codeazur.com.br', 'http://jonasgalvez.com.br')

import re
import unittest

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

class XNCondition(Storage):
  BASIC_OPERATORS = ('<>', '<=', '>=', '<', '>', '=')
  CONDITION = re.compile("""^[^=><]*(.*?)['"]*$""")
  LINE_STRIP_QUOTES = re.compile("""^['"]*(.*?)['"]*$""")
  def __init__(self, operator, leftside, rightside):
    self.operator = operator
    self.leftside = leftside
    stripped = XNCondition.LINE_STRIP_QUOTES.match(rightside)
    if stripped: self.rightside = stripped.group(1)
    else: self.rightside = rightside
  @staticmethod
  def parse(fromstring):
    for op in XNCondition.BASIC_OPERATORS:
      operands = fromstring.split(op)
      if len(operands) > 1:
        return XNCondition(op, *map(str.strip, operands))
    return None

class XNQuery:
  ENTITY_AND_CONDITIONS = re.compile("""([^(]+)(?:\((.*)\))?""")
  def __init__(self, entities, order):
    self.entities = Storage()
    self.order = Storage()
    self._parse_entities(entities)
    self._parse_conditions(self.order, order)
  def _parse_entities(self, entities):
    entities = entities.split('/')
    for entity in entities:
      m = XNQuery.ENTITY_AND_CONDITIONS.match(entity)
      if m:
        entity_name = m.group(1)
        self.entities[entity_name] = Storage()
        entity_obj = self.entities[entity_name]
        conds = m.group(2)
        if conds:
          entity_obj.conditions = Storage()
          self._parse_conditions(entity_obj.conditions, conds)
  def _parse_conditions(self, obj, conditions):
    if conditions == None:
      return None
    for cond in conditions.split('&'):
      xncond = XNCondition.parse(cond)
      if xncond: obj[xncond.leftside] = xncond

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
    xnquery = XNQuery(sample_query[0], sample_query[1])
    assert xnquery.entities['content'].conditions['author'].rightside == 'david'
  def test_order_parsing(self):
    sample_query = self.queries[3]
    xnquery = XNQuery(sample_query[0], sample_query[1])
    assert xnquery.order['order'].rightside == 'my.viewCount@D'

if __name__ == '__main__':
  unittest.main()