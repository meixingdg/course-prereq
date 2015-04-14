import re
import hashlib
#from string import letters - not recognizing string.letters ???
import string
import random


secret = 'vn39zjn02z93kfnzw3kn'

#validate form fields--------------------------------------------------------

#create regular expression object from regular expression pattern
#do this to use matching methods: match() and search() 
#http://docs.python.org/2/library/re.html#re.compile
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")  
def valid_username(username): 
	#check if valid using above defined regular expression
	return username and USER_RE.match(username)
	
PASSWORD_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
	return password and PASSWORD_RE.match(password)
	
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_email(email):
	return not email or EMAIL_RE.match(email)
	
#validate cookie-------------------------------------------------------------	
	
#returns a hashed param w/ format:
#user_id|HASH(user_id+salt)
def make_secure_val(val):
	h = hashlib.sha256(val+secret).hexdigest()
	return '%s|%s' % (val, h)

#check if the cookie (secure_val) is valid, returns a boolean
def check_secure_val(secure_val): 
    val = secure_val.split('|')[0]
    return secure_val == make_secure_val(val)
	
#validate login---------------------------------------------------------------
def make_salt(): #make a string of 5 random letters using python's random module
	return ''.join(random.choice(string.letters) for x in xrange(5))
	
def make_pw_hash(name, pw, salt=None):
	if not salt:
		salt=make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s|%s' % (salt, h)

def valid_pw(name, pw, h):
	salt = h.split('|')[0]
	return h == make_pw_hash(name, pw, salt)