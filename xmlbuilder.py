from __future__ import with_statement

__author__ = ('Jonas Galvez', 'jonas@codeazur.com.br', 'http://jonasgalvez.com.br')

import sys

class builder:
  def __getattr__(self, name):
    return element(name)

class element:
  def __init__(self, name):
    self.name = name
  def __enter__(self):
    if hasattr(self, 'attributes'):
      print '<%s %s>' % (self.name, self.serialized_attrs)
    else:
      print '<%s>' % self.name
  def __exit__(self, type, value, tb):
    print '</%s>' % self.name
  def __call__(self, value=None, **kargs):
    if len(kargs.keys()) > 0:
      self.attributes = kargs
      self.serialized_attrs = self.serialize_attrs(kargs)
    if value != None:
      if hasattr(self, 'attributes'):
        print '<%s %s>%s</%s>' % (self.name, self.serialized_attrs, value, self.name)
      else:
        print '<%s>%s</%s>' % (self.name, value, self.name)
      return
    return self
  def serialize_attrs(self, attrs):
    serialized = []
    for attr, value in attrs.items():
      serialized.append('%s="%s"' % (attr, value))
    return ' '.join(serialized)

xml = builder()

with xml.entries:
  with xml.entry(id=1):
    xml.title("Woohoo!")

'''
<entries>
<entry id="1">
<title>Woohoo!</title>
</entry>
</entries>
'''
