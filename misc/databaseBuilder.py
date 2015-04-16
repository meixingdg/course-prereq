import sqlite3
import json
import urllib

# Url for the YACS API.
YACSURL = "http://yacs.me/api/4/"

# Function to send a request to YACS, and load the json it sends backs.
# Input: yacsUrl - a string that holds the YACS url to open
# Output: the data in the json returned by YACS.
# Called by: runner(dbName)
def getYacsJsonResponse(yacsUrl):
    yacsResponse = urllib.urlopen(yacsUrl)
    jsonData = json.loads(yacsResponse.read())
    return jsonData

# Function to add a semester's worth of data into our database.
# Input:
#     dbName - a string that holds our database's name.
#     coursesJsonData - the data loaded from a json from YACS that holds courses information.
#     semester - a string that holds the semester of the courses we loaded.
#             Can be either "Spring," "Summer," or "Fall."
#     year - an integer that holds the year of the courses.
# Called by: runner(dbName)
def addJsonToDb(dbName, coursesJsonData, semester, year):
    db = sqlite3.connect(dbName)
    cursor = db.cursor()    
    for row in coursesJsonData["result"]:
        if row["name"] != "":

            # Add each course in the json into our table.
            try:
                cursor.execute('''INSERT INTO
                        courses(semester, year, name, number, description, isCommIntense,
                                minCredits, gradeType, maxCredits,
                                prereqs, departmentId)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (semester, year, row["name"], row["number"], row["description"], row["is_comm_intense"],
                        row["min_credits"], row["grade_type"], row["max_credits"],
                        row["prereqs"], row["department_id"]))

            # We skip any courses that cause an error.
            # An error is caused when a course's semester, year, and number match one already in the table.
            except sqlite3.IntegrityError:
                 print "Course " + str(row["id"]) + " in " + semester + " " + str(year) + " is already in the database."

    db.commit()
    db.close()

# Function to create the courses table in our database given a database name.
# Input: dbName - a string that holds our database's name.
# Called by: runner(dbName)
def createCoursesTable(dbName):
    db = sqlite3.connect(dbName)
    cursor = db.cursor()

    # We use course semester, year, and number as our keys.
    cursor.execute('''CREATE TABLE IF NOT EXISTS
            courses(semester TEXT, year INTEGER, name TEXT, number INTEGER, description TEXT, isCommIntense INTEGER,
                    minCredits INTEGER, gradeType TEXT, maxCredits INTEGER,
                    prereqs TEXT, departmentId INTEGER, PRIMARY KEY (semester, year, number))''')

    db.commit()
    db.close()

# Function to run all other functions.
# Creates a new database and puts the courses of every semester available in YACS into it.
# Input: dbName - a string that holds our database's name.
def runner(dbName):
    createCoursesTable(dbName)

    # Get the json of semesters from YACS and load it.
    semestersJsonData = getYacsJsonResponse(YACSURL + "semesters/")

    # We go through each semester and get the semester id, year, and season.
    for row in semestersJsonData["result"]:
        semesterId = row["id"]
        year = row["year"]
        semester = row["name"].split(" ")[0]

        # We request the courses of a given semester from YACS and add the data to our database.
        yacsSemesterUrl = YACSURL + "courses/?semester_id=" + str(semesterId) + "/" 
        jsonData = getYacsJsonResponse(yacsSemesterUrl)
        addJsonToDb(dbName, jsonData, semester, year)

runner("test.db")
