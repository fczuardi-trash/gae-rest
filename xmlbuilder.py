__author__ = ('Jonas Galvez', 'jonas@codeazur.com.br', 'http://jonasgalvez.com.br')

from __future__ import with_statement
import sys

class GeneratorContextManager(object):
  def __init__(self, gen):
    self.gen = gen
  def __enter__(self):
    try:
      return self.gen.next()
    except StopIteration:
      raise RuntimeError("generator didn't yield")
  def __exit__(self, type, value, traceback):
    if type is None:
      try:
        self.gen.next()
      except StopIteration:
        return
      else:
        raise RuntimeError("generator didn't stop")
    else:
      try:
        self.gen.throw(type, value, traceback)
        raise RuntimeError("generator didn't stop after throw()")
      except StopIteration:
        return True
      except:
        if sys.exc_info()[1] is not value:
          raise

def contextmanager(ref, name, func):
  def helper(*args, **kwds):
    if len(args) > 0:
      ref.write_element(name, args[0])
    else:
      return GeneratorContextManager(func(*args, **kwds))
  return helper

class XMLBuilder:
  def __init__(self):
    self.document = ""
  def __getattr__(self, name):
    return contextmanager(self, name, self._element_writer(name))
  def _element_writer(self, name):
    ref = self
    def _write_element_generator(value=None):
      try:
        ref.document += '<%s>' % name
        if value != None:
          ref.document += value
        yield
      finally:
        ref.document += '</%s>' % name
    return _write_element_generator
  def write_element(self, name, value):
    self.document += '<%s>%s</%s>' % (name, value, name)

##### USAGE #####

xml = XMLBuilder()
entries = [{'name': 'Entry #1'}, {'name': 'Entry #2'}]

# pretty sweet, huh?
with xml.entries():
  for entry in entries:
    xml.entry(entry['name'])

print xml.document
'''
result:

<entries><entry>Entry #1</entry><entry>Entry #2</entry></entries>
'''