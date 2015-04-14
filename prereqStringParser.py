import string
import sys

def splitReqStrUsingAndOr(rawStr, debug = False):
	# list of strings that are split by ands
	andStrs = rawStr.split(' and ')

	if debug:
		print 'and-ed strings: ', andStrs

	# split each of the and-ed strings by or
	andStrs = [strng.split(' or ') for strng in andStrs]

	if debug:
		print 'or-ed string: ', andStrs


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
	indices[1] = rawStr.find('corerequisite')

	if debug:
		print 'raw string: %s' % (rawStr)
		print 'indices: ', indices

	if indices[0] == -1 and indices[1] == -1:
		# if neither of the strings were found, then assume all of the courses contained in the string are prerequisites
		prereqStr = rawStr
	elif indices[0] == -1 and indices[1] != -1:
		# if only corequisite found, then assume all of the courses contained in the string are corequisites
		coreqStr = rawStr
	elif indices[0] != -1 and indices[1] == -1:
		# if only prerequisite found, then assume all of the courses contained in the string are prerequisites
		prereqStr = rawStr
	else:
		# if both of the strings were found, then split the raw string accordingly
		if indices[0] < indices[1]:
			# the prereq portion is the string that is before 'corequisite' was found
			prereqStr = rawStr[:indices[1]]
			coreqStr = rawStr[indices[1]:]
		else:
			# the coreq portion is the string that is before 'prerequisite' was found
			coreqStr = rawStr[:indices[0]]
			prereqStr = rawStr[indices[0]:]

	if debug:
		print 'coreqStr: %s' % (coreqStr)
		print 'prereqStr: %s' % (prereqStr)




if __name__ == '__main__':
	string = "Prerequisites:  ARCH 4140, ARCH 4330 and ARCH  4560; A pre or corequisite to ARCH 4300."
	prereqParser(string, True)





