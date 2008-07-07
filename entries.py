from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api.users import User
from datetime import datetime
import wsgiref.handlers

class Entry(db.Model):
  user = db.UserProperty()
  published = db.DateTimeProperty()

entries = ['jonasgalvez@gmail.com', 'fabricio@gmail.com']

for entry in Entry.all():
  entry.delete()

for entry in entries:
  e = Entry(user=User(email=entry), published=datetime.now())
  e.put()

class EntriesHandler(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'plain/text'
    entries = db.GqlQuery("SELECT * FROM Entry")
    for entry in entries:
      self.response.out.write("entry = %s\n" % repr(entry))
      self.response.out.write("entry.user.nickname = %s\n" % entry.user.nickname())
      self.response.out.write("entry.user.email = %s\n--\n" % entry.user.email())

def main():
  application = webapp.WSGIApplication([('/entries.*', EntriesHandler)], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()