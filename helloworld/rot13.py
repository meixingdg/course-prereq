import webapp2

form="""
<form method="post">
	Enter some text to ROT13:
	<br>
	<input type="textarea" name="text" value="%(prev_text)s">
	<br>
	<input type="submit">
</form>
"""


import cgi
def validate(text):
	ascii_text = list() #empty list to store every letter of the text in ascii
	for character in text:
		ascii = ord(character)
		
		#if is capital letter
		if ascii >= 65 and ascii <=90: 
			ascii = ascii+13
			if ascii > 90: #loop around
				ascii = 65 + (ascii-90-1)
				
		#if is lower case letter
		elif ascii >=97 and ascii <=122:
			ascii = ascii+13
			if ascii > 122: #loop around
				ascii = 97 + (ascii-122-1)
		else: #anything else
			ascii = ord(character)
		ascii_text.append(ascii) #store in list
	
	#convert all back to characters
	for x in range(0, len(ascii_text)):
		ascii_text[x] = chr(ascii_text[x])
	#make back into a single string
	result = ''.join(ascii_text)
	#escape html 
	return cgi.escape(result, quote=True)


class Rot13_handler (webapp2.RequestHandler):
	def write_form(self, prev_text=""):
		self.response.out.write(form %{"prev_text": prev_text} )
	
	def get(self):
		self.write_form()
	
	def post(self):
		#get what was input into the form
		input_text = self.request.get("text")
		input_text = validate(input_text)
		self.write_form(input_text) 
		#validate input and do Rot13

app = webapp2.WSGIApplication([('/rot13', Rot13_handler)], debug=True)