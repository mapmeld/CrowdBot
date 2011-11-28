import cgi

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

# user views of CrowdBot
class CrowdBotIn(webapp.RequestHandler):
  def get(self):
	# live stream homepage
	if(self.request.get('screen') == 'watch'):
		self.response.out.write('''<!DOCTYPE html>
<html>
	<head>
		<title>Watch CrowdBot</title>
	</head>
	<body>
		<h1>CrowdBot Live Streaming</h1>
		Programs are submitted online through <a href="/crowdbot?screen=send" target="_blank">this form</a>.
	</body>
</html>''')
	else:
		# form to submit sketches
		self.response.out.write('''<!DOCTYPE html>
<html>
	<head>
		<title>CrowdBot Sketch Entry</title>
	</head>
	<body>
		<h1>CrowdBot Sketch Entry</h1>
		<form accept-charset="UTF-8" action="/crowdbot" method="post">
			<h3>Give your Twitter or e-mail address for us to send the video</h3>
			<input name="identify"/>
			<h3>Name your Sketch</h3>
			<input name="sketchname"/>
			<h3>Enter Sketch</h3>
			<textarea name="mysketch"></textarea>
			<br/>
			<input type="submit" value="Send Sketch"/>
		</form>
	</body>
</html>''')

  def post(self):
	# store a sketch and redirect to the livestream page
	sketch = CrowdBotProgram()
	sketch.programname = self.request.get('sketchname')
	sketch.username = self.request.get('identify')
	sketch.programtext = db.Text(self.request.get('mysketch'))
	sketch.hasRun = 'False'
	sketch.put()
	self.redirect('/crowdbot?screen=watch')

# API requests from the crowdbot-host machine
class CrowdBotOut(webapp.RequestHandler):
  def get(self):
	# simply output an un-run sketch ( will be updated to include more information about user, sketch name )
	sketch = CrowdBotProgram().gql("WHERE hasRun = 'False'").get()
	self.response.out.write(sketch.programtext)

# current data model for user-submitted sketches
class CrowdBotProgram(db.Model):
	programname = db.StringProperty(multiline=False)
	username = db.StringProperty(multiline=False)
	programtext = db.TextProperty()
	hasRun = db.StringProperty(multiline=False)

# webapp framework within AppEngine
application = webapp.WSGIApplication([('/crowdbot/out',CrowdBotOut),
									('/crowdbot.*',CrowdBotIn)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()