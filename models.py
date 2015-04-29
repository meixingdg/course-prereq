from google.appengine.ext import ndb

class Course(ndb.Model):
    code = ndb.IntegerProperty()
    departmentCode = ndb.StringProperty()
    departmentName = ndb.StringProperty()
    description = ndb.TextProperty()
    gradeType = ndb.StringProperty()
    isCommIntense = ndb.BooleanProperty()
    maxCredits = ndb.IntegerProperty()
    minCredits = ndb.IntegerProperty()
    name = ndb.StringProperty()
    prereqs = ndb.TextProperty()
    semester = ndb.StringProperty()
    year = ndb.IntegerProperty()

class Department(ndb.Model):
    code = ndb.StringProperty()
    name = ndb.StringProperty()
