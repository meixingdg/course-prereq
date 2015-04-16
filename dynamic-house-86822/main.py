import webapp2
import urllib
import json
import jinja2
import os

from models import Course
from google.appengine.ext import ndb
from prereqStringParser import *

#Temporarily hardcoded a list of department codes.
DEPARTMENTCODES = ["ADMN", "ARCH", "ARTS", "ASTR",
        "BCBP", "BIOL", "BMED", "CHEM",
        "CHME", "CIVL", "COGS", "COMM",
        "CSCI", "ECON",
        "ECSE", "ENGR", "ENVE", "EPOW",
        "IENV", "IHSS", "ISCI", "ISYE",
        "ITWS", "LANG", "LGHT", "LITR",
        "MANE", "MATH", "MATP", "MGMT",
        "MTLE", "PHIL", "PHYS", "PSYC",
        "STSH", "STSS", "USAF", "USAR",
        "USNA", "WRIT"]

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def getStuff(dep, code): 
    entry = ndb.gql("SELECT * FROM Course WHERE departmentCode = '" + dep + "' and code = " + code)
    return entry.fetch(1)

def buildPrereqTree(dep, code, tree, depth=0):
    course = getStuff(dep, code)
    for i in course:
        tree.append((depth, i.name, i.code, i.departmentCode))
        prereqs = getCourses(i.prereqs)
        for preorco in prereqs:
            for orclause in preorco:
                for singleCourse in orclause:
                    listCourse = splitCourseString(singleCourse)
                    dep2 = listCourse[0].upper()
                    code2 = listCourse[1]
                    buildPrereqTree(dep2, code2, tree, depth + 1)
    
class MainHandler(webapp2.RequestHandler):
    
    def get(self):
        departments = DEPARTMENTCODES
        courses = []
        template_values = {'departments': departments}
        template = JINJA_ENVIRONMENT.get_template('templates/selectDep.html')
        self.response.write(template.render(template_values))
        
    def post(self):
        reset = self.request.get('reset')
        course = self.request.get('course')
        department = self.request.get('department')

        #If the user hit the reset button, we go back to let the user
        #repick the department.
        if reset == "true":
            self.get()
            
        #If we do not obtain a course from the post, the user
        #must have only selected a department.
        elif course == "":
            self.department = department
            self.courseSelect(department)

        #Otherwise, we have the department and course
        else: self.outputPrereqs(department, course)

    def courseSelect(self, department):

        departments = [department]
        entry = Course.query(Course.departmentCode == department)
        courses = []
        for course in entry:
            courses.append(str(course.code) + " - " + course.name)
        courses.sort()
        template_values = {
            'departments': departments,
            'courses': courses
        }
        template = JINJA_ENVIRONMENT.get_template('templates/selectCourse.html')
        self.response.write(template.render(template_values))

    def outputPrereqs(self, department, course):
        tree = []
        code = course[:4]
        buildPrereqTree(department, code, tree)
        template_values = {
            'tree': tree
        }
        template = JINJA_ENVIRONMENT.get_template('templates/outputPrereqs.html')
        self.response.write(template.render(template_values))

    
#    #def courseDFS(self, dep, courseInput, depth=0):
#    #    code = courseInput.split('-')[0]
#    #    course = getStuff(dep, code)       
#    #    for i in course:
#    #        #name = (i.name).encode(
#    #        self.response.write('<font color=ffffff>'+'_' * 4 * depth + '</font>' + i.name + '<br>')
#    #        prereqs = getCourses(i.prereqs)
#    #        for preorco in prereqs:
#    #            for orclause in preorco:
#    #                  for singleCourse in orclause:
#    #                    listCourse = splitCourseString(singleCourse)
#    #                    dep2 = listCourse[0].upper()
#    #                    code2 = listCourse[1]
#    #                    self.courseDFS(dep2, code2, depth + 1)
#    #    if depth == 0:
#    #        self.reponse.write('<button name="reset" value ="true" type="submit">Reset</button><hr>')
                   
app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)

    
