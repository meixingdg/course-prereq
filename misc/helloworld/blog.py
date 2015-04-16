import webapp2
import jinja2
import datetime
from google.appengine.ext import db

import os
import re
	
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
							   
class Entry(db.Model):
	title = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	
	def as_dict(self):
		time_format = '%c'
		dict = {'subject': self.title,
				'content': self.content,
				'created': self.created.strftime(time_format)}
		return dict
	
class FrontPage(BaseHandler):
	def get(self):
		posts_ = db.GqlQuery('SELECT * FROM Entry ORDER BY created ASC')
		#self.response.out.write(posts_.count())
		self.render('blog_frontpage.html', posts = posts_)
		#self.render('blog_frontpage.html')
		
class NewPost(BaseHandler):
	def get(self):
		self.render('blog_newpost.html')
		
	def post(self):
		title_ = self.request.get('subject')
		content_ = self.request.get('content')
		
		params = {'prev_title':title_, 'prev_content':content_}
		
		has_error = False
		if not title_ or not content_:
			has_error = True
			params['error_message'] = 'Both subject and content are required.'
		
		if has_error:
			self.render('blog_newpost.html', **params)
		else:
			#make instance of post, put into database
			post = Entry(title=title_, content=content_)
			post.put()
			post_id = str(post.key().id())
			self.redirect('/blog/%s' %post_id)
			
class PermPost(BaseHandler):
	def get(self, post_id):
		p = Entry.get_by_id(int(post_id))
		if p:
			self.render('blog_permalink.html', post=p)
		else:
			self.response.out.write("This post was not found. :(")
	
app = webapp2.WSGIApplication([('/blog/?(?:\.json)?', FrontPage), 
								('/blog/newpost/', NewPost),
								('/blog/([0-9]+)(?:\.json)?', PermPost)], #parentheses mean whatever is here is passed into get or post function
								debug=True)