import cgi

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

# user views of CrowdBot
class CrowdBotIn(webapp.RequestHandler):
  def get(self):
	if(self.request.get('screen') == 'watch'):
		# live stream homepage
		self.response.out.write('''<!DOCTYPE html>
<html>
	<head>
		<title>Watch CrowdBot</title>
	</head>
	<body>
		<table><tr><td>
			<h1>CrowdBot Live Streaming</h1>
			<iframe src="http://www.ustream.tv/embed/9893969" width="608" height="368" scrolling="no" frameborder="0" style="border: 0px none transparent;"></iframe>
		</td><td>
			<div>
				<p>Programs are submitted online through <a href="/crowdbot?screen=send" target="_blank">this form</a>.</p>
				<iframe src="/crowdbot/out?status=live" width="200" height="400" scrolling="no" frameborder="0" style="border: 0px none transparent;"></iframe>
			</div>
		</td></tr></table>
	</body>
</html>''')
	else:
		# form to submit sketches
		self.response.out.write('''<!DOCTYPE html>
<html>
	<head>
		<title>CrowdBot Test Entry</title>
		<script type="text/javascript">
function writeSample(){
	document.getElementById("sketchplace").value = "/*\\n  Blink\\n  Turns on an LED on for two seconds, then off for five seconds, repeatedly.\\n */\\nvoid setup() {\\n  pinMode(13, OUTPUT);\\n}\\nvoid loop() {\\n  digitalWrite(13, HIGH);\\n  delay(2000);\\n  digitalWrite(13, LOW);\\n  delay(5000);\\n}";
}
		</script>
	</head>
	<body>
		<h1>CrowdBot Test Entry</h1>
		<table><tr><td>
			<form accept-charset="UTF-8" action="/crowdbot" method="post" style="border-right:1px solid silver;margin-right:15px;padding-right:15px;">
				<h3>Your e-mail address <strike>or Twitter</strike> for us to send the video</h3>
				<input name="identify" width="300"/>
				<h3>Name your Sketch</h3>
				<input name="sketchname" width="300"/>
				<h3>Enter Sketch or <a href='#' onclick='writeSample()'>Sample</a></h3>
				<textarea id="sketchplace" name="mysketch" width="400" height="600" rows="18" cols="60"></textarea>
				<br/>
				<input type="submit" value="Send Sketch"/>
			</form>
		</td><td>
			<div style="margin-left:15px;">
				<a href="/crowdbot?screen=watch" target="_blank">Watch the livestream now</a>
			</div>
		</td></tr></table>
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
	if(self.request.get('status') == 'live'):
		# print out a mini-page about the current program, which refreshes every few minutes by default
		self.response.out.write('''<!DOCTYPE html>
<html>
	<head>
		<meta http-equiv="refresh" content="180"/>
		<title>Current CrowdBot Program</title>
	</head>
	<body>\n''')
		livesketch = CrowdBotProgram().gql("WHERE hasRun = 'True' ORDER BY uploaded DESC").get()
		if(livesketch is not None):
			self.response.out.write(cgi.escape(livesketch.programname) + '<hr/>')
			self.response.out.write(cgi.escape(livesketch.programtext.replace('\n','<br/>')))
		else:
			self.response.out.write('No program loaded\n')
		self.response.out.write('''	</body>
</html>''')
	else:
		# simply output an un-run sketch ( will be updated to include more information about user, sketch name )
		sketch = CrowdBotProgram().gql("WHERE hasRun = 'False' ORDER BY uploaded ASC").get()
		self.response.out.write(sketch.programtext)
		livesketch = CrowdBotProgram().gql("WHERE hasRun = 'True' ORDER BY uploaded DESC").get()
		if(livesketch is not None):
			livesketch.delete()
		sketch.hasRun = 'True'
		sketch.put()

# current data model for user-submitted sketches
class CrowdBotProgram(db.Model):
	programname = db.StringProperty(multiline=False)
	username = db.StringProperty(multiline=False)
	programtext = db.TextProperty()
	hasRun = db.StringProperty(multiline=False)
	uploaded = db.DateTimeProperty(auto_now=True)

# webapp framework within AppEngine
application = webapp.WSGIApplication([('/crowdbot/out',CrowdBotOut),
									('/crowdbot.*',CrowdBotIn)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()