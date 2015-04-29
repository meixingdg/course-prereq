import webapp2
import urllib
import json
import jinja2
import os

from models import Course
from models import Department
from google.appengine.ext import ndb
from courseparser import CourseParser

colors = ["#FE642E","#8181F7","#DA81F5","#D0FA58","#58FAF4","#FA5858","#FE2EC8"]

class CourseNode():
    def __init__(self,baseCourse, depth = 0, color = "#FF0000"):
        self.backgroundColor = color
        self.depth = depth
        self.name = baseCourse.name
        self.departmentCode = baseCourse.departmentCode
        self.code = baseCourse.code
        
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
        node = CourseNode(i, depth, colors[color%len(colors)])
        tree.append(node)
        prereqs = CourseParser.get_courses(i.prereqs)
        for preOrCo in prereqs:
            color +=1
            for orClause in preOrCo:
                color +=1
                for singleCourse in orClause:
                    listCourse = splitCourseString(singleCourse)
                    dep2 = listCourse[0].upper()
                    code2 = listCourse[1]
                    buildPrereqTree(dep2, code2, tree, depth + 1, color)
                    

def get_menu_template_values():
    templateValues = dict()
    depEntries = Department.query().order(Department.code)
    depCodes = []
    depNames = []
    depCourses = []
    
    for dep in depEntries:
        courses = []
        #courses.append(dep.code.encode('utf8'))        
        depCodes.append(dep.code.encode('utf8'))
        depNames.append(dep.name.encode('utf8'))
        courseEntries = Course.query(Course.departmentCode == dep.code)
        for course in courseEntries:
            courses.append(str(course.code) + " - " + course.name.encode('utf8'))
        courses.sort()
        courses.insert(0, dep.code.encode('utf8'))
        depCourses.append(courses)
    
    templateValues["depCodes"] = depCodes
    templateValues["depNames"] = depNames
    templateValues["depCourses"] = depCourses
    return templateValues

class MainHandler(webapp2.RequestHandler):
    
    def get(self):
        #self.templateValues = get_template_values()
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.write(template.render(menu_template_values))
        
    def post(self):
        reset = self.request.get('reset')
        course = self.request.get('course')
        department = self.request.get('department')

        #If the user hit the reset button, we go back to let the user
        #repick the department.
        if reset == "true":
            self.get()

        elif course == "" or department == "":
            self.get()
            
        #Otherwise, we have the department and course
        else: self.outputPrereqs(department, course)


    def outputPrereqs(self, department, course):
        tree = []
        code = course[:4]
        buildPrereqTree(department, code, tree)
        template_values = {
            'tree': tree
        }
        template = JINJA_ENVIRONMENT.get_template('templates/outputPrereqs.html')
        self.response.write(template.render(template_values))


menu_template_values = get_menu_template_values()
app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)

    
