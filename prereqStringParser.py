import string
import sys
import re

def splitReqStrUsingAndOr(rawStr, debug = False):
	# convert to lower case to make parsing easier, in case it wasn't already done
	rawStr = rawStr.lower()

	# replace tabs and multiple spaces w/ spaces 
	rawStr = re.sub('[\t ]+', ' ', rawStr)

	# list of strings that are split by ands
	andStrs = re.split(' and |,', rawStr)

	if debug:
		print 'and-ed strings: ', andStrs

	# split each of the strings by comma
	commaedStrs = [strng.split(' or ') for strng in andStrs]

	# split each of the and-ed strings by or
	orStrs = [strng.split(' or ') for strng in andStrs]

	if debug:
		print 'or-ed string: ', orStrs

	courseRegex = re.compile(r"([a-z]{4} [0-9]{4})")
	courses = [[]]*len(orStrs)
	# extract the courses from each of the or-ed strings
	for orStrListInd in range(len(orStrs)):
		convertedList = []
		for rawCourseStr in orStrs[orStrListInd]:
			convertedList.extend([foundCourse.group() for foundCourse in re.finditer(courseRegex, rawCourseStr)])
		courses[orStrListInd] = convertedList
	return courses


def splitStrIntoPrereqAndCoreq(rawStr, debug = False):
	# convert to lower case to make parsing easier
	rawStr = rawStr.lower()

	# split into prereqs and coreqs first
	prereqStr = ""
	coreqStr = ""

	# find words ('prerequisite' or 'prerequisites') and ('corequisite' or corequisites')
	# 	indices[0] - index where the string "prerequisite" is found in rawStr
	#	indices[1] - index where the string "corerequisite" is found in rawStr
	indices = [0]*2
	indices[0] = rawStr.find('prerequisite')
	indices[1] = rawStr.find('corequisite')
	regex = re.compile(r"[.;]")

	# get first index of a delimiter
	delimiterInd = -1
	for a in regex.finditer(rawStr):
		delimiterInd = a.start()
		break

	if debug:
		print 'raw string: %s' % (rawStr)
		print 'string match indices: ', indices
		print 'delimiter index: ', delimiterInd

	if indices[0] == -1 and indices[1] == -1:
		if debug:
			print 'case 1'
		# if neither of the strings were found, then assume all of the courses contained in the string are prerequisites
		if delimiterInd == -1:
			delimiterInd = len(rawStr)
		prereqStr = rawStr[:delimiterInd]
	elif indices[0] == -1 and indices[1] != -1:
		if debug:
			print 'case 2'
		# if only corequisite found, then assume all of the courses contained in the string are corequisites that are behind the coreq substring match
		coreqStr = rawStr[indices[1]:]
		prereqStr = rawStr[:indices[1]]
	elif indices[0] != -1 and indices[1] == -1:
		if debug:
			print 'case 3'
		# if only prerequisite found, then assume all of the courses contained in the string are prerequisites, up to delimiter
		prereqStr = rawStr[:delimiterInd]
	else:
		# if both of the strings were found, then split the raw string accordingly
		# 	- the first portion, whichever that is, will end where a delimiter is found (., ;, or 'corequisite')
		if indices[0] < indices[1]:
			# the prereq portion is the string that is before 'corequisite' was found, up to a delimiter
			prereqStr = rawStr[:delimiterInd]
			coreqStr = rawStr[indices[1]:] 
		else:
			# the coreq portion is the string that is before 'prerequisite' was found
			coreqStr = rawStr[:delimiterInd]
			prereqStr = rawStr[indices[0]:]

	if debug:
		print 'coreqStr: %s' % (coreqStr)
		print 'prereqStr: %s' % (prereqStr)

	return prereqStr, coreqStr

'''
takes "econ 2010" --> ['econ','2010']
'''
def splitCourseString(courseStr):
	splitStr = courseStr.split()
	return splitStr 

''' 
Returns courses = [[[p1, p2], [p3], [p4]], [[c1, c2], [c3]]]
	where p1 = a course string like 'econ 2010'
courses[0] = prerequisites
	each list in courses[0] is a group of prerequisites
		if the list has more than one course, only one is required (this or that)
courses[1] = corequisites
	see description for courses[0], change to corequisites
'''
def getCourses(rawStr, debug = False):
	prereqStr, coreqStr = splitStrIntoPrereqAndCoreq(rawStr, debug)
	prereqCourses = splitReqStrUsingAndOr(prereqStr, debug)
	coreqCourses = splitReqStrUsingAndOr(coreqStr, debug)
	if debug:
		print 'original string: ', rawStr
		print 'prereq courses: ', prereqCourses
		print 'coreq courses: ', coreqCourses
	return [prereqCourses, coreqCourses] 
if __name__ == '__main__':
	string1 = "Prerequisites:  ARCH 4140 and ARCH 4330 or ARCH  4560; A pre or corequisite to ARCH 4300."
	string2 = 'ARCH 2530 Digital Constructs 2, Corequisites: ARCH 2800 Architectural Design Studio 1'
	string3 = 'Prerequisite: COMM 4420, COMM 4770, or COMM 4710.'
	string4 = 'CSCI 2500 or ECSE 2660, and CSCI 1200. Experience with database systems recommended.'
	print getCourses(string4, False)
	#prereqStr, coreqStr = splitStrIntoPrereqAndCoreq(string, True)
	#print 'prereq ----------------- '
	#splitReqStrUsingAndOr(prereqStr, True)



