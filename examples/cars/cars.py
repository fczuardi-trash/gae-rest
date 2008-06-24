from google.appengine.ext import db
from google.appengine.ext import webapp

class Car(db.Model):
  name = db.StringProperty(required=True)
  manufacturer = db.StringProperty()

cars = [
  ('VW', 'Golf'),
  ('GM', 'Astra')
]

for car in Car.all():
  car.delete()

for car in cars:
  c = Car(name=car[0], manufacturer=car[1])
  c.put()

class CarsHandler(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'plain/text'
    cars = db.GqlQuery("SELECT * FROM Car")
    for car in cars:
      self.response.out.write("car.name = %s\n" % car.name)
      self.response.out.write("car.manufacturer = %s\n--" % car.manufacturer)
