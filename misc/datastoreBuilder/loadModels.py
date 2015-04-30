from google.appengine.ext import db

class Department(db.Model):
    code = db.StringProperty()
    name = db.StringProperty()

class Course(ndb.Model):
    code = db.IntegerProperty()
    departmentCode = db.StringProperty()
    departmentName = db.StringProperty()
    description = db.TextProperty()
    gradeType = db.StringProperty()
    isCommIntense = db.BooleanProperty()
    maxCredits = db.IntegerProperty()
    minCredits = db.IntegerProperty()
    name = db.StringProperty()
    prereqs = db.TextProperty()
    semester = db.StringProperty()
    year = db.IntegerProperty()
