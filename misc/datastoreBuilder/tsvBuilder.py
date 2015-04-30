import json
import urllib

# We keep global variables to store the YACS API's urls.
yacs_url = "http://yacs.me/api/4/"
yacs_deps_url = yacs_url + "departments/"
yacs_courses_url = yacs_url + "courses/"

def get_deps():
    """Get a json of departments from YACS."""
    
    response = urllib.urlopen(yacs_deps_url)
    data = json.loads(response.read())
    return data["result"]

def get_courses(depId = None):
    """Function to get a json of courses from YACS.
    If a department id is passed in, we get only the courses from that department.
    """

    if depId == None:
        response = urllib.urlopen(yacs_courses_url)
    else:
        response = urllib.urlopen(yacs_courses_url + "?department_id=" + str(depId))
    data = json.loads(response.read())
    return data["result"]

def make_deps_tsv(outFileName):
    """Function to create a tsv file.
    The tsv will have the department code, name.
    """

    depsData = get_deps()
    outFileObj = open(outFileName, 'w')
    for dep in depsData:
        outFileObj.write(dep["code"] + "\t" + dep["name"] + "\n")

def create_departments_dict():
    """Function to create a dictionary in which the YACS department
    ID is the key and the department name and code is the value.
    """

    departmentsJsonResult = get_deps()
    departmentsDict = dict()
    for row in departmentsJsonResult:
        departmentsDict[row["id"]] = (row["name"], row["code"])
    return departmentsDict

def make_courses_tsv(semester, year, outFileName):
    """Function to create a tsv file of course info."""

    departmentsDict = create_departments_dict()
    coursesData = get_courses()
    outFile = open(outFileName, 'w')
    for row in coursesData:
        outFile.write(semester + "\t"
                + year + "\t"
                + row["name"].encode('utf8') + "\t"
                + str(row["number"]) + "\t"
                + row["description"].encode('utf8') + "\t"
                + str(row["is_comm_intense"]) + "\t"
                + str(row["min_credits"]) + "\t"
                + row["grade_type"].encode('utf8') + "\t"
                + str(row["max_credits"]) + "\t"
                + row["prereqs"].encode('utf8') + "\t"
                + departmentsDict[row["department_id"]][0].encode('utf8') + "\t"
                + departmentsDict[row["department_id"]][1].encode('utf8') + "\n")
    outFile.close()
    
make_deps_tsv("tdeps.tsv")
make_courses_tsv("Fall", "2015", "tcourses.tsv")
