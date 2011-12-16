import cgi

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api.urlfetch import POST
import crowdbotconfig
import twitteroauth

# main views of CrowdBot
class CrowdBotIn(webapp.RequestHandler):
  def get(self):
	if(self.request.get('screen') == 'watch'):
		# livestream of Arduino
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
				<iframe src="/crowdbot/out?status=live" width="300" height="400" scrolling="yes" frameborder="0" style="border: 0px none transparent;"></iframe>
			</div>
		</td></tr></table>
	</body>
</html>''')
	else:
		# submit a sketch
		self.response.out.write('''<!DOCTYPE html>
<html>
	<head>
		<title>CrowdBot Test Entry</title>
		<script type="text/javascript">
function writeSample(){
	//document.getElementById("sketchplace").value = "/*\\n  Blink\\n  Turns on an LED on for two seconds, then off for five seconds, repeatedly.\\n */\\nvoid setup() {\\n  pinMode(13, OUTPUT);\\n}\\nvoid loop() {\\n  digitalWrite(13, HIGH);\\n  delay(2000);\\n  digitalWrite(13, LOW);\\n  delay(5000);\\n}";
	document.getElementById("sketchplace").value = "/*\\n  Blink\\n  Turns on blue and yellow LEDs on for four seconds, then off for two seconds, repeatedly.\\n  pin 2 is blue\\n  pin 4 is green\\n  activating #2 and #4 together makes one aqua-green light\\n  pin 6 is yellow\\n  pin 13 is indicator on Arduino\\n */\\nvoid setup() {\\n  pinMode(2, OUTPUT);\\n  pinMode(6, OUTPUT);\\n}\\nvoid loop() {\\n  digitalWrite(2, HIGH);\\n  digitalWrite(6, HIGH);\\n  delay(4000);\\n  digitalWrite(2, LOW);\\n  digitalWrite(6, LOW);\\n  delay(2000);\\n}";
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
	# accept a new sketch from the form
	sketch = CrowdBotProgram()
	sketch.programname = self.request.get('sketchname')
	sketch.username = self.request.get('identify')
	sketch.programtext = db.Text(self.request.get('mysketch'))
	sketch.hasRun = 'False'
	sketch.put()
	self.redirect('/crowdbot?screen=watch')

# API requests
class CrowdBotOut(webapp.RequestHandler):
  def get(self):
	if(self.request.get('status') == 'live'):
		# print out a mini-page about the current program, which refreshes every few minutes by default
		self.response.out.write('''<!DOCTYPE html>
<html>
	<head>
		<meta http-equiv="refresh" content="180"/>
		<title>Current CrowdBot Program</title>
		<style type="text/css">
html, body{
	font-family: courier;
}
		</style>
	</head>
	<body>\n''')
		# find the last sketch to be downloaded to the board - print program name and source code
		livesketch = CrowdBotProgram().gql("WHERE hasRun = 'True' ORDER BY uploaded DESC").get()
		if(livesketch is not None):
			self.response.out.write(cgi.escape(livesketch.programname) + '<hr/>')
			self.response.out.write(cgi.escape(livesketch.programtext.replace('\n','<br/>')).replace('&lt;br/&gt;','<br/>').replace(' ','&nbsp;'))
		else:
			self.response.out.write('No program loaded\n')
		self.response.out.write('''		<br/>
		<input type="button" value="Refresh" onclick="location.reload(true)"/>
	</body>
</html>''')
	else:
		# output the earliest-submitted pending sketch ( will be updated to include more information about user, sketch name )
		sketch = CrowdBotProgram().gql("WHERE hasRun = 'False' ORDER BY uploaded ASC").get()
		livesketch = CrowdBotProgram().gql("WHERE hasRun = 'True' ORDER BY uploaded DESC").get()
		if(sketch is not None):
			self.response.out.write(sketch.programtext)
			# move pending sketch to live
			sketch.hasRun = 'True'
			sketch.put()
			if(livesketch is not None):
				# move live sketch to 'Complete'
				livesketch.hasRun = 'Complete'
				livesketch.put()

			# send Tweets to authors of latest and next sketch, if Twitter was provided
			# based on Anil Shanbhag's Twitter Bot: http://anilattech.wordpress.com/2011/10/29/making-a-twitter-bot-using-appengine/
			if(sketch.username.find('@') == 0):

				finished_format = "%s: your sketch has finished running on our #CrowdBot"
				starting_format = "%s: your sketch will run on our #CrowdBot for the next 3+ minutes"

				# oauth client released by Mike Knapp (see twitteroauth.py for more information)
				client = twitteroauth.TwitterClient(crowdbotconfig.consumer_key, crowdbotconfig.consumer_secret, crowdbotconfig.callback_url)

				additional_params = {
					"status": starting_format % (sketch.username)
				}
				result = client.make_request(
					"http://twitter.com/statuses/update.json",
					token=crowdbotconfig.access_token,
					secret=crowdbotconfig.access_token_secret,
					additional_params=additional_params,
					method=POST)
				#logging.info(result.content)
		else:
			# there are no pending programs
			self.response.out.write('no new program')

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