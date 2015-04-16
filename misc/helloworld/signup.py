import validation

import webapp2
import jinja2
#import cgi #html escaping
import datetime
from google.appengine.ext import db

import os

#creating database entity
class User(db.Model):
	_username = db.StringProperty(required = True)
	_password = db.StringProperty(required = True)
	_email = db.StringProperty(required = False)
	_created = db.DateTimeProperty(auto_now_add = True)
	#_salt = db.StringProperty(required = True)

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
							
def str_render(template, **params):
	#t is a jinja Template class instance
	t = jinja_env.get_template(template)
	#render/write out the resulting HTML using Template class member function
	#http://jinja.pocoo.org/docs/api/
	return t.render(params) 

class BaseHandler(webapp2.RequestHandler):
	def render(self, template, **params):
		#use the str_render function to turn our html template into jinja Template,
			#then write out with the error messages
		#if params is empty, then no errors will be printed
		self.response.out.write(str_render(template, **params))
	
class Signup_handler(BaseHandler):
	def get(self):
		self.render("signup_page.html")
	
	def post(self):
		#.get() returns values for arguments parsted from the query and from POST data
			#takes argument name as the first paramenter
		#http://webapp-improved.appspot.com/guide/request.html
		#all inputs are html escaped
		username = self.request.get("username")
		password = self.request.get("password")
		verify = self.request.get("verify")
		email = self.request.get("email")
		
		has_error = False
		
		#store the newly-input username and email
		params = {'prev_username':username, 'prev_email':email}
		
		#add to the template parameters the error messages if the error exists
		if not validation.valid_username(username):
			params['username_error'] = "That's not a valid username."
			has_error = True
		else:
			#check if user already exists
			#for queries w/ variables: https://developers.google.com/appengine/docs/python/datastore/gqlqueryclass
			matches = db.GqlQuery('SELECT * FROM User WHERE _username = :1', username)
			if matches.count() != 0:
				has_error = True
				params['username_error'] = 'That account already exists!'
			
		if not validation.valid_password(password):
			params['password_error'] = "That wasn't a valid password."
			has_error = True
		elif password != verify:
			params['verify_error'] = "Your passwords didn't match."
			has_error = True
		
		if not validation.valid_email(email):
			params['email_error'] = "That's not a valid email."
			has_error = True
		
		if has_error:
			self.render("signup_page.html", **params)
		else:
			#put user in database
			#user = User(_username=username, _password=password, _email=email)
			#hash the password before storing
			password = validation.make_pw_hash(username, password)
			user = User(_username=username, _password=password, _email=email)
			user.put()
			#self.redirect("/welcome?username=" + username)
			
			#get the id of the user
			user_id = str(user.key().id())
			#hash the id
			h_user_id = validation.make_secure_val(user_id)
			#set a cookie
			self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/' % h_user_id)
			self.redirect("/welcome")
		
class Success_handler(BaseHandler):
	def get(self):
		#username = self.request.get('username')
		#get username from cookie
		user_cookie = self.request.cookies.get('user_id', '')
		#self.response.out.write(user_id)
		
		if validation.check_secure_val(user_cookie):
			#if the cookie is valid, retrieve username from database
			user_id = user_cookie.split('|')[0]
			user = User.get_by_id(int(user_id))
			self.render('signup_success.html', username=user._username)
		else:
			#cookie was not valid, redirect to signup page
			self.redirect('/signup')
		'''
		if validation.valid_username(username):
			self.render('signup_success.html', username = username)
		else:
			self.redirect("/signup")
		'''
		
class DisplayUsers(BaseHandler):
	def get(self):
		users_ = db.GqlQuery("SELECT * FROM User ORDER BY _created ASC")
		#self.response.out.write(users_.count())
		self.render('all_users.html', users = users_)
		
class Login(BaseHandler):
	def get(self):
		self.render('login.html')
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		has_error = False
		params = {'prev_username':username}
		#check if user in database
		match = db.GqlQuery('SELECT * FROM User WHERE _username=:1', username)
		if match.count() == 0:
			#user is not in database, invalid login
			has_error = True
		else:
			#get password hash from database, hash the given username and password with salt from db, verify
			#.get() gets the first single matching entity found
			account = match.get()
			h_pw = account._password
			#if the information is correct, direct to welcome page and set cookie
			if validation.valid_pw(username, password, h_pw):
				#get the id of the user
				user_id = str(account.key().id())
				#hash the id
				h_user_id = validation.make_secure_val(user_id)
				#set a cookie
				self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/' % h_user_id)
				self.redirect("/welcome")
			else:
				has_error = True
		
		if has_error:
			params['error_message'] = 'Invalid login.'
			self.render('login.html', **params)
			
class Logout(BaseHandler):
	def get(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=''; Path=/')
		self.redirect('/signup')

app = webapp2.WSGIApplication([('/signup', Signup_handler), 
								('/welcome', Success_handler), 
								('/users', DisplayUsers), 
								('/login', Login),
								('/logout', Logout)],
								debug=True)