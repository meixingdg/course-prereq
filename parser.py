import string
import sys
import re

class Parser():
    @classmethod
    def _split_req_str_using_and_or(cls, rawStr, debug=False):
        # Convert to lower case to make parsing easier, in case it wasn't already done
        rawStr = rawStr.lower()

        # Replace tabs and multiple spaces w/ spaces 
        rawStr = re.sub('[\t ]+', ' ', rawStr)

        # List of strings that are split by ands
        andStrs = rawStr.split(' and ')

        if debug:
            print 'and-ed strings: ', andStrs

        # Split each of the and-ed strings by or
        orStrs = [strng.split(' or ') for strng in andStrs]

        if debug:
            print 'or-ed string: ', orStrs

        # Split remaining strings by comma
        for i in range(len(orStrs)):
            orStrs[i] = [strng.split(',') for strng in orStrs[i]]
            # Flatten the list
            orStrs[i] = [strng[0] for strng in orStrs[i]]

        if debug:
            print 'after split using commas: ', orStrs

        courseRegex = re.compile(r"([a-z]{4} [0-9]{4})")
        courses = [[]]*len(orStrs)

        # Extract the courses from each of the or-ed strings
        for orStrListInd in range(len(orStrs)):
            convertedList = []
            for rawCourseStr in orStrs[orStrListInd]:
                convertedList.extend([foundCourse.group() \
                                    for foundCourse in re.finditer(courseRegex, rawCourseStr)])
            courses[orStrListInd] = convertedList
        
        return courses

    @classmethod
    def _split_str_into_prereq_and_coreq(cls, rawStr, debug=False):
        # Convert to lower case to make parsing easier
        rawStr = rawStr.lower()

        # Split into prereqs and coreqs first
        prereqStr = ""
        coreqStr = ""

        # Find words ('prerequisite' or 'prerequisites') and ('corequisite' or corequisites')
        #   indices[0] - index where the string "prerequisite" is found in rawStr
        #   indices[1] - index where the string "corerequisite" is found in rawStr
        indices = [0]*2
        indices[0] = rawStr.find('prerequisite')
        indices[1] = rawStr.find('corequisite')
        regex = re.compile(r"[.;]")

        # Get first index of a delimiter
        delimiterInd = -1
        for a in regex.finditer(rawStr):
            delimiterInd = a.start()
            break

        if indices[0] == -1 and indices[1] == -1:
            # If neither of the strings were found, then assume all of the courses contained 
            # in the string are prerequisites.
            if delimiterInd == -1:
                delimiterInd = len(rawStr)
            prereqStr = rawStr[:delimiterInd]
        elif indices[0] == -1 and indices[1] != -1:
            # If only corequisite found, then assume all of the courses contained in the string 
            # are corequisites that are behind the coreq substring match.
            coreqStr = rawStr[indices[1]:]
            prereqStr = rawStr[:indices[1]]
        elif indices[0] != -1 and indices[1] == -1:
            # If only prerequisite found, then assume all of the courses contained in the string
            # are prerequisites, up to delimiter.
            prereqStr = rawStr[:delimiterInd]
        else:
            # If both of the strings were found, then split the raw string accordingly
            #   - the first portion, whichever that is, will end where 
            #       a delimiter is found (., ;, or 'corequisite')
            if indices[0] < indices[1]:
                # The prereq portion is the string that is before 'corequisite' was found, 
                # up to a delimiter.
                prereqStr = rawStr[:delimiterInd]
                coreqStr = rawStr[indices[1]:] 
            else:
                # The coreq portion is the string that is before 'prerequisite' was found.
                coreqStr = rawStr[:delimiterInd]
                prereqStr = rawStr[indices[0]:]

        if debug:
            print 'coreqStr: %s' % (coreqStr)
            print 'prereqStr: %s' % (prereqStr)

        return prereqStr, coreqStr

    """
    Takes a course string and returns the split string as a list
    #
    ex. split_course_string('econ 2010') returns ['econ','2010']
    """
    @classmethod
    def split_course_string(cls, courseStr):
        splitStr = courseStr.split()
        return splitStr 
    
    """
    Takes a raw string and returns a list of the courses.
    #
    The return list is formatted as such: 
    [[[p_1, p_2], [p_3], [p_4]], [[c_1, c_2], [c_3]]]
    where p_x are prerequisites and c_x are corequisites.
    #
    The first element of the returned list is a list containing the prerequisites. 
    Each element of that list is a set of requirements, where only one course of 
    a set needs to be taken. The second element, also a list, in the returned list 
    follows the same convention except for corequisites.
    """
    @classmethod
    def get_courses(cls, rawStr, debug=False):
        if rawStr == None:
            return [[],[]]
        prereqStr, coreqStr = cls._split_str_into_prereq_and_coreq(rawStr, debug)
        prereqCourses = cls._split_req_str_using_and_or(prereqStr, debug)
        coreqCourses = cls._split_req_str_using_and_or(coreqStr, debug)
        return [prereqCourses, coreqCourses] 

if __name__ == '__main__':
    string1 = "Prerequisites:  ARCH 4140 and ARCH 4330 or ARCH  4560; A pre or corequisite to ARCH 4300."
    string2 = 'ARCH 2530 Digital Constructs 2, Corequisites: ARCH 2800 Architectural Design Studio 1'
    string3 = 'Prerequisite: COMM 4420, COMM 4770, or COMM 4710.'
    print Parser.get_courses(string2, True)
    prereqStr, coreqStr = Parser._split_str_into_prereq_and_coreq(string1, True)
    print 'prereq ----------------- '
    Parser._split_req_str_using_and_or(prereqStr, True)
    print Parser.get_courses(None)

