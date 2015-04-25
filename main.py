import webapp2
import urllib
import json
import jinja2
import os

from models import Course
from google.appengine.ext import ndb
from prereqStringParser import *

colors = ["#FE642E","#8181F7","#DA81F5","#D0FA58","#58FAF4","#FA5858","#FE2EC8"] #temporary hardcoded list of colors - easily expandable

class CourseNode(): #just a simple class for use with jinja that keeps track of needed attributes for rendering the tree
    def __init__(self,baseCourse, depth = 0, color = "#FF0000"):
        self.backgroundColor = color
        self.depth = depth
        self.name = baseCourse.name
        self.departmentCode = baseCourse.departmentCode
        self.code = baseCourse.code
        

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

def buildPrereqTree(dep, code, tree, depth=0, color = 0):
    course = getStuff(dep, code)
    for i in course: #getStuff returns a singleton list of courses
        node = CourseNode(i, depth, colors[color%len(colors)]) #builds a node out of what we got from getStuff,
                                                               #with depth of whatever we're at and the next color, looping if needed
        prereqs = getCourses(i.prereqs) #parses the prereqs string into the form [PREREQS, COREQS] where PREREQS 
                                        #is a list consisting of [ORCLAUSE, ORCLAUSE], ORCLAUSE is a list of 
                                        #[COURSE1, COURSE2] and COURSE is a list of [depcode, code]. COREQ is
                                        #the same as prereq 
        for preOrCo in prereqs: #goes into PREREQS and then COREQS
            color +=1           
            for orClause in preOrCo: #Each ORCLAUSE shares a color
                color +=1
                for singleCourse in orClause:
                    listCourse = splitCourseString(singleCourse) #finds depcode and code, then continues the DFS
                    dep2 = listCourse[0].upper()
                    code2 = listCourse[1]
                    buildPrereqTree(dep2, code2, tree, depth + 1, color)
    
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
                   
app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)

    
