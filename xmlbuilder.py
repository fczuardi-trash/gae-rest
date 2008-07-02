from __future__ import with_statement
from StringIO import StringIO

__author__ = ('Jonas Galvez', 'jonas@codeazur.com.br', 'http://jonasgalvez.com.br')

import sys

class builder:
  def __init__(self):
    self.document = StringIO()
    self.indentation = -2
  def __getattr__(self, name):
    return element(name, self)
  def __str__(self):
    return self.document.getvalue()
  def write(self, line):
    self.document.write('%s%s' % ((self.indentation * ' '), line))

class element:
  def __init__(self, name, builder):
    self.name = name
    self.builder = builder
  def __enter__(self):
    self.builder.indentation += 2
    if hasattr(self, 'attributes'):
      self.builder.write('<%s %s>\n' % (self.name, self.serialized_attrs))
    else:
      self.builder.write('<%s>\n' % self.name)
  def __exit__(self, type, value, tb):
    self.builder.write('</%s>\n' % self.name)
    self.builder.indentation -= 2
  def __call__(self, value=None, **kargs):
    if len(kargs.keys()) > 0:
      self.attributes = kargs
      self.serialized_attrs = self.serialize_attrs(kargs)
    if value != None:
      self.builder.indentation += 2
      if hasattr(self, 'attributes'):
        self.builder.write('<%s %s>%s</%s>\n' % (self.name, self.serialized_attrs, value, self.name))
      else:
        self.builder.write('<%s>%s</%s>\n' % (self.name, value, self.name))
      self.builder.indentation -= 2
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
    xml.ref("//1")
  with xml.entry(id=2):
    xml.title("Woohoo!")
    xml.ref("//2")

print xml

'''
<entries>
<entry id="1">
<title>Woohoo!</title>
</entry>
</entries>
'''