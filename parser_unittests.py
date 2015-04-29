import unittest
from courseparser import CourseParser 

class TestParsePrereqCoreqSplit(unittest.TestCase):

    # Test passing in empty string.
    def test_prereq_coreq_split_t1(self):  
        testStr = ''
        prereqStr, coreqStr = CourseParser._split_str_into_prereq_and_coreq(testStr)
        self.assertEqual(prereqStr, '')
        self.assertEqual(coreqStr, '')

    # Test passing in a string that only has prerequisites,
    # with the prerequisite label at the beginning of the string.
    def test_prereq_coreq_split_t2(self):
        testStr = "Prerequisites:  ARCH 4140 and ARCH 4330."
        prereqStr, coreqStr = CourseParser._split_str_into_prereq_and_coreq(testStr)
        self.assertEqual(prereqStr, "prerequisites:  arch 4140 and arch 4330.")
        self.assertEqual(coreqStr, "")

    # Test passing in a string that only has corequisites, 
    # with the corequisite label at the beginning of the string.
    def test_prereq_coreq_split_t3(self):
        testStr = "Corequisites: ARCH 2800 Architectural Design Studio 1"
        prereqStr, coreqStr = CourseParser._split_str_into_prereq_and_coreq(testStr)
        self.assertEqual(prereqStr, "")
        self.assertEqual(coreqStr, "corequisites: arch 2800 architectural design studio 1")

    # Test passing in a string that has both prerequisites and corequisites, 
    # with both labels clearly present in the string.
    def test_prereq_coreq_split_t4(self):
        testStr = "Prerequisites: ENGR 1100 and PHYS 1100. Corequisite: MATH 2400."
        prereqStr, coreqStr = CourseParser._split_str_into_prereq_and_coreq(testStr)
        self.assertEqual(prereqStr, "prerequisites: engr 1100 and phys 1100.")
        self.assertEqual(coreqStr, "corequisite: math 2400.")

    # Test passing in a string that has corequisites but "corequisite" is spelled as "co-requisite"
    def test_prereq_coreq_split_t5(self):
        testStr = "Co-requisite: Students in ARCH 4980 are required to co-register."
        prereqStr, coreqStr = CourseParser._split_str_into_prereq_and_coreq(testStr)
        self.assertEqual(prereqStr, "")
        self.assertEqual(coreqStr, "co-requisite: students in arch 4980 are required to co-register.")

    # Test passing in a string that has courses that are both pre and corequisites. 
    # This test is for when only "corequisite" is written out.
    def test_prereq_coreq_split_t6(self):
        testStr = "Pre-or corequisite: ENGR 2600."
        prereqStr, coreqStr = CourseParser._split_str_into_prereq_and_coreq(testStr)
        self.assertEqual(prereqStr, "pre-or ")
        self.assertEqual(coreqStr, "corequisite: engr 2600.")

    # Test passing in a string that has courses that are both pre and corequisites. 
    # This test is for when both "prerequisite" and "corequisite" are written out.
    def test_prereq_coreq_split_t7(self):
        testStr = "Prerequisite or corequisite: ENGR 2600."
        prereqStr, coreqStr = CourseParser._split_str_into_prereq_and_coreq(testStr)
        self.assertEqual(prereqStr, "prerequisite or corequisite: engr 2600.")
        self.assertEqual(coreqStr, "corequisite: engr 2600.")

    # Test passing in a string that has no valid courses.
    def test_prereq_coreq_split_t8(self):
        testStr = "None"
        prereqStr, coreqStr = CourseParser._split_str_into_prereq_and_coreq(testStr)
        self.assertEqual(prereqStr, "none")
        self.assertEqual(coreqStr, "")

    # Test passing in None.
    def test_prereq_coreq_split_t9(self):
        testStr = None
        prereqStr, coreqStr = CourseParser._split_str_into_prereq_and_coreq(testStr)
        self.assertEqual(prereqStr, "")
        self.assertEqual(coreqStr, "")

    # Test passing in string without explicit tags.
    def test_prereq_coreq_split_t10(self):
        testStr = "ARCH 2830 Architectural Design Studio 4, and ARCH 4780 Architectural Design Studio 6."
        prereqStr, coreqStr = CourseParser._split_str_into_prereq_and_coreq(testStr)
        self.assertEqual(prereqStr, "arch 2830 architectural design studio 4, and arch 4780 architectural design studio 6.")
        self.assertEqual(coreqStr, "")

class TestSplitAndOr(unittest.TestCase):

    # Test passing in None.
    def test_split_and_or_t1(self):
        testStr = None
        self.assertEqual(CourseParser._split_req_str_using_and_or(testStr), [[]])

    # Test passing in empty string.
    def test_split_and_or_t2(self):
        testStr = ''
        self.assertEqual(CourseParser._split_req_str_using_and_or(testStr), [[]])

    # Test passing in a string with just ands.
    def test_split_and_or_t3(self):
        testStr = 'Prerequisites:  ARCH 4140 and ARCH 4330.'
        self.assertEqual(CourseParser._split_req_str_using_and_or(testStr), [['arch 4140'], ['arch 4330']])

    # Test passing in a string with just ors.
    def test_split_and_or_t4(self):
        testStr = 'Prerequisites:  ARCH 4140 or ARCH 4330.'
        self.assertEqual(CourseParser._split_req_str_using_and_or(testStr), [['arch 4140', 'arch 4330']])

    # Test passing in a string with both ands and ors.
    def test_split_and_or_t5(self):
        testStr = 'Prerequisites:  ARCH 4140 and ARCH 4330 or ARCH 4560.'
        self.assertEqual(CourseParser._split_req_str_using_and_or(testStr), [['arch 4140'], ['arch 4330', 'arch 4560']])

    # Test passing in a string with ands, ors, and commas.
    def test_split_and_or_t6(self):
        testStr = 'Prerequisites: ARCH 4820, and ARCH 4330 or ARCH 4740.'
        self.assertEqual(CourseParser._split_req_str_using_and_or(testStr), [['arch 4820'], ['arch 4330', 'arch 4740']])

class TestGetCourses(unittest.TestCase):
    def test_get_courses_t1(self):
        testStr = "Prerequisites:  ARCH 4140 and ARCH 4330 or ARCH 4560; A pre or corequisite to ARCH 4300."
        courses = CourseParser.get_courses(testStr)
        self.assertEqual(courses, [[['arch 4140'], ['arch 4330', 'arch 4560']], [['arch 4300']]])

if __name__ == '__main__':
    unittest.main()