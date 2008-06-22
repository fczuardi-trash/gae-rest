from google.appengine.ext import db

class Car(db.Model):
  name = db.StringProperty(required=True)
  manufacturer = db.StringProperty()
