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

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
	
class CourseNode():
    """This is an extremely simple class used only to store data for retrieval by 
    the template.
    """

    def __init__(self,baseCourse, depth = 0, color = "#FF0000"):
        self.backgroundColor = color
        self.depth = depth
        self.name = baseCourse.name
        self.departmentCode = baseCourse.departmentCode
        self.code = baseCourse.code
        self.description = baseCourse.description
        self.prereqs = baseCourse.prereqs

def get_stuff(dep, code):
    """This function returns a singleton list containing a course.
    keyword arguments:
    dep -- deparment code
    code -- intradepartment identification code
    """

    entry = ndb.gql("SELECT * FROM Course WHERE departmentCode = '" + dep + "' and code = " + code)
    return entry.fetch(1)

def build_prereq_tree(dep = 'CSCI', code = '4440', tree = [], depth=0, color = 0):
    """This function builds a prereq tree.
    Keyword arguments:
    dep -- the department code (default 'CSCI')
    code -- the course identifier in a department (default '4440'
    tree -- the list of courses (default [])
    depth -- how many ancestors the function has (default 0) do not change
    color -- an index for the color list (default 0)
    """

    course = get_stuff(dep, code)
    for i in course: 
        node = CourseNode(i, depth, colors[color%len(colors)])
        tree.append(node)
        prereqs = CourseParser.get_courses(node.prereqs)


        #Loops over the list of lists returned by get_courses. Although
        #it looks horribly inefficient, it actually only accesses each
        #element once- the course list is structured oddly, to preserve
        #distinction between ANDS and ORS and PREREQS and COREQS.
        for preOrCo in prereqs:
            color +=1
            for orClause in preOrCo:
                color +=1
                for singleCourse in orClause:
                    listCourse = CourseParser.split_course_string(singleCourse)
                    dep2 = listCourse[0].upper()
                    code2 = listCourse[1]
                    build_prereq_tree(dep2, code2, tree, depth + 1, color)
                    
def get_menu_template_values():
    """Builds a list of department name, department codes, a list of lists.
    The inner list in this list of lists are of course names and codes.
    The first element of these lists are the department code of these courses.
    This is to pass menu values to the ui.
    """

    templateValues = dict()
    depCodes = []
    depNames = []
    depCourses = []


    # Query the datastore for the full list of departments.
    # We go through each department and store its name and code.
    depEntries = Department.query().order(Department.code)
    for dep in depEntries:
        courses = []
        depCodes.append(dep.code.encode('utf8'))
        depNames.append(dep.name.encode('utf8'))

        # Query the datastore for the courses in our current department.
        # We add a string representing each course to a list.
        courseEntries = Course.query(Course.departmentCode == dep.code)
        for course in courseEntries:
            courses.append(((str(course.code) + " - " + course.name).encode('utf8')).replace("\xe2\x80\x99" ,"'"))
        courses.sort()
        courses.insert(0, dep.code.encode('utf8'))
        depCourses.append(courses)

    templateValues["depCodes"] = depCodes
    templateValues["depNames"] = depNames
    templateValues["depCourses"] = depCourses
    return templateValues

class MainHandler(webapp2.RequestHandler):
    	
    def get(self):
        """Initially the MainHandler outputs this."""

        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.write(template.render(menu_template_values))

    def post(self):
        """When the MainHandler gets a response, we look at the values given to us.
        If the user hit the reset button, we restart the application.
        If the user failed to submit either a course or a department, we restart.
        Otherwise, we have the department and course, and we make our tree.
        """

        reset = self.request.get('reset')
        course = self.request.get('course')
        department = self.request.get('department')
        if reset == "true":
            self.get()
        elif course == "" or department == "":
            self.get()
        else: 
            self.output_prereqs(department, course)

    def output_prereqs(self, department, course):
        """If we have been given a department and course from the user, the main handler builds
        the tree and sends it to the user.
        """

        tree = []
        code = course[:4]
        build_prereq_tree(department, code, tree)
        template_values = {
            'tree': tree
        }
        template = JINJA_ENVIRONMENT.get_template('templates/outputPrereqs.html')
        self.response.write(template.render(template_values))

#We create the menu template values here so that we only do it once on start up.
menu_template_values = get_menu_template_values()
app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
