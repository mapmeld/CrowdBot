import cgi

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api.urlfetch import POST
from google.appengine.api import channel, mail
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
			<!-- UStream embed code -->
			<iframe src="http://www.ustream.tv/embed/9893969" width="500" height="350" scrolling="no" frameborder="0" style="border: 0px none transparent;"></iframe>
			<!-- Test Justin.TV embed
			<object type="application/x-shockwave-flash" height="350" width="500" id="live_embed_player_flash" data="http://www.justin.tv/widgets/live_embed_player.swf?channel=crowdbot" bgcolor="#000000">
				<param name="allowFullScreen" value="true" />
				<param name="allowScriptAccess" value="always" />
				<param name="allowNetworking" value="all" />
				<param name="movie" value="http://www.justin.tv/widgets/live_embed_player.swf" />
				<param name="flashvars" value="hostname=www.justin.tv&channel=crowdbot&auto_play=false&start_volume=25" />
			</object> -->
			<br/>
			<iframe src="/crowdbot/out?get=livedata" width="400" height="300" scrolling="yes" frameborder="0" style="border:0px none transparent;"></iframe>
		</td><td>
			<div>
				<button onclick="window.location='/crowdbot';" style="font-size:18pt">
					<img src="/gear.jpg" style="vertical-align:middle;" height="18pt" width="18pt"/>
					Reprogram CrowdBot
				</button><br/>
				<iframe src="/crowdbot/out?get=livecode" width="400" height="500" scrolling="yes" frameborder="0" style="border: 0px none transparent;"></iframe>
			</div>
		</td></tr></table>
	</body>
</html>''')
	else:
		# submit a sketch
		self.response.out.write('''<!DOCTYPE html>
<html>
	<head>
		<title>CrowdBot Entry</title>
		<script type="text/javascript">
function init(){
	$("dostream").checked = true;
	$("dosend").checked = false;
}
function writeSample(){
	var sketch = "";
	switch($("samples").value){
		case "blink":
			sketch = "/*\\n  Blink Test\\n  Turns blue and yellow LEDs on and off, repeatedly.\\n  pin 2 is blue\\n  pin 4 is green\\n  activating 2 and 4 together makes aqua-green\\n  pin 6 is yellow\\n  pin 8 is purple\\n  pin 13 is orange indicator on Arduino\\n */\\nvoid setup() {\\n  /* at start, prepare LED pins */\\n  pinMode(2, OUTPUT);\\n  pinMode(4, OUTPUT);\\n  pinMode(6, OUTPUT);\\n  pinMode(8, OUTPUT);\\n  pinMode(13, OUTPUT);\\n}\\nvoid loop() {\\n  /* program a light show here! */\\n  digitalWrite(2, HIGH);\\n  digitalWrite(6, HIGH);\\n  digitalWrite(8,LOW);\\n  /* wait 3 seconds with those settings */\\n  delay(3000);\\n  digitalWrite(2, LOW);\\n  digitalWrite(6, LOW);\\n  digitalWrite(8,HIGH);\\n  /* wait 2 seconds with those settings */\\n  delay(2000);\\n  /* loop() repeats */\\n}";
			break;
		case "sensor":
			sketch = "/* Sensor Test\\n  Turns purple LED on whenever sensor detects the yellow LED\\n  digital pin 6 is yellow\\n  digital pin 8 is purple\\n  pin 12 is light sensor\\n*/\\nint onIn = 1;\\nint lightSense;\\nvoid setup(){\\n  pinMode(6, OUTPUT);\\n  pinMode(8, OUTPUT);\\n}\\nvoid loop(){\\n  // cycle the target light\\n  // target light is on 0.5 seconds out of 2\\n  onIn = onIn + 1;\\n  if(onIn % 5 == 0){\\n    digitalWrite(6, HIGH);\\n    onIn = 1;\\n  }\\n  else{\\n    digitalWrite(6, LOW);\\n  }\\n  lightSense = analogRead(1);\\n  if(lightSense < 800){\\n    // target light detected! purple LED on!\\n    digitalWrite(8, HIGH);\\n  }\\n  else{\\n    // target light off! purple LED off!\\n    digitalWrite(8, LOW);\\n  }\\n  delay(500);\\n}";
			break;
		case "hello":
			sketch = "/* Stream Test\\nCrowdBot data stream test\\nsays \\"hello\\" then random numbers */\\nvoid setup(){\\n  Serial.begin(9600);\\n  Serial.println(\\"hello\\");\\n  // read unconnected analog pin 0 for randomizing noise\\n  randomSeed( analogRead(0) );\\n}\\nvoid loop(){\\n  Serial.println( random(1, 101) );\\n  delay(1000);\\n}";
			break;
		case "random":
			sketch = "/* Random Blink\\n  blinks blue, green, and purple for random intervals */\\nvoid setup(){\\n  // prepare blink lights\\n  pinMode(2, OUTPUT);\\n  pinMode(4, OUTPUT);\\n  pinMode(8, OUTPUT);\\n  // read unconnected analog pin 0 for randomizing noise\\n  randomSeed( analogRead(0) );\\n}\\nvoid loop(){\\n  digitalWrite(2, HIGH);\\n  delay( random(750, 2001) );\\n  digitalWrite(2, LOW);\\n  digitalWrite(4, HIGH);\\n  delay( random(750, 2001) );\\n  digitalWrite(4, LOW);\\n  digitalWrite(6, HIGH);\\n  delay( random(750, 2001) );\\n  digitalWrite(6, LOW);\\n  delay( random(750, 1001) );\\n}";
			break;
		case "streamer":
			sketch = "/* Data Streamer\\n  streams light sensor value to CrowdBot\\n  target light is pink LED with variable analog value */\\nint lightSense;\\nint lightCycle = 1;\\nvoid setup(){\\n  pinMode(9, OUTPUT);\\n  Serial.begin(9600);\\n  randomSeed( analogRead(0) );\\n}\\nvoid loop(){\\n  // set the light LED to a random value every 4 seconds\\n  if(lightCycle % 5 == 0){\\n    lightCycle = 1;\\n    analogWrite(9, random(20,250) );\\n  }\\n  else{\\n    lightCycle = lightCycle + 1;\\n  }\\n  // read the light sensor every second\\n  lightSense = analogRead(3);\\n  Serial.println( lightSense );\\n  delay(1000);\\n}";
			break;
		case "current":
			var s = document.createElement("script");
			s.src = "/crowdbot/out?get=current&jsonp=update";
			s.type = "text/javascript";
			document.body.appendChild(s);
			return;
			break;
	}
	$("sketchplace").value = sketch;	
}
function update(currentSketch){
	while(currentSketch.indexOf("|~|") > -1){
		currentSketch = currentSketch.replace("|~|","\\n");
	}
	$("sketchplace").value = currentSketch;
}
function $(id){
	return document.getElementById(id);
}
		</script>
		<style type="text/css">
ul.spacedlist li{
	margin-bottom:10px;
}
		</style>
	</head>
	<body onload="init()">
		<table><tr><td>
			<form accept-charset="UTF-8" action="/crowdbot" method="post" style="border-right:1px solid silver;margin-right:15px;padding-right:15px;">
				<h1>Program CrowdBot</h1>
				<h3 style="display:inline;margin-right:20px;">Tweetable Sketch Name</h3>
				<input name="sketchname" width="300"/>
				<h3>Optional contact:<br/>
				Twitter (@mapmeld) or e-mail (you@example.com)</h3>
				<input name="identify" width="400" size="30"/>
				<br/>
				<h3 style="display:inline;margin-right:20px;">Data streaming</h3>
				<label>
					<input id="dostream" type="checkbox" name="dostream" checked="checked"/>
					Stream data?
				</label>
				<label>
					<input id="dosend" type="checkbox" name="dosend"/>
					Send data?
				</label>				
				<h3>
					Write Sketch or Select
					<select id='samples' href='#' onchange='writeSample()'>
						<option value="none">-</option>
						<option value="blink">Blink Test</option>
						<option value="sensor">Sensor Test</option>
						<option value="hello">Stream Test</option>
						<option value="random">Random Blink</option>
						<option value="streamer">Data Streamer</option>
						<option value="current">Current Sketch</option>
					</select>
				</h3>
				<textarea id="sketchplace" name="mysketch" width="400" height="600" rows="18" cols="60"></textarea>
				<br/>
				<input type="submit" value="Send Sketch"/>
			</form>
		</td><td>
			<div style="margin-left:15px;">
				<button onclick="window.location='/crowdbot?screen=watch';" style="font-size:16pt">
					<img src="/camera.jpg" style="vertical-align:middle;" height="18pt" width="18pt"/>
					Watch livestream
				</button>
				<h3>Reference</h3>
				<ul class="spacedlist" style="font-family:courier;list-style:none;">
					<li>analogRead( PIN# )<br/>return pin value from 0 (0V) to 1024 (5V)</li>
					<li>analogWrite( PIN# , 0 <= val <= 255 )<br/>activates the pin to 0-5V</li>
					<li>delay( milliseconds )<br/>wait before continuing to the next line</li>
					<li>digitalRead( PIN# )<br/>return pin as HIGH or LOW</li>
					<li>digitalWrite( PIN# , HIGH or LOW )<br/>sets the pin to 5V or 0V / GND</li>
					<li>pinMode( PIN# , INPUT or OUTPUT )<br/>sets a pin to read or write information</li>
					<li>Serial.begin( 9600 )<br/>connect computer and Arduino over USB/serial port</li>
					<li>Serial.println( # or "" )<br/>output a message (number or text) to the computer</li>
					<li>Serial.println("DONE")<br/>start the next program</li>
				</ul>
			</div>
		</td></tr></table>
	</body>
</html>''')

  def post(self):
	if(self.request.get('livedata') != ''):
		# update live data
		channel.send_message('crowdbot_data', cgi.escape(self.request.get('livedata')))
	elif(self.request.get('mail') != ''):
		# send saved data
		logging.info(self.request.get('mail'))
		sketch = CrowdBotProgram.get_by_id(long(self.request.get('id')))
		sketch.feed = db.Text(self.request.get('data'))
		sketch.put()
		
		if(self.request.get('mail').find('@') == 0):
			# Twitter name
			if(self.request.get('data').replace('\n','').replace(' ','').replace('	','') == ''):
				# no data recorded
				finished_format = "%s: #CrowdBot ran your sketch, '%s'. No data was returned"
			else:
				# send data record
				finished_format = "%s: #CrowdBot ran your sketch, '%s'. Data stored at http://mapmeld.com/crowdbot/out?get=feed&id=" + self.request.get('id')

			# oauth client released by Mike Knapp (see twitteroauth.py for more information)
			client = twitteroauth.TwitterClient(crowdbotconfig.consumer_key, crowdbotconfig.consumer_secret, crowdbotconfig.callback_url)
			additional_params = {
				"status": finished_format % (sketch.username.replace(' ',''), sketch.programname.replace('@','').replace('#','').replace('/',''))
			}
			result = client.make_request(
				"http://twitter.com/statuses/update.json",
				token=crowdbotconfig.access_token,
				secret=crowdbotconfig.access_token_secret,
				additional_params=additional_params,
				method=POST)
			#logging.info(result.content)
		elif(self.request.get('mail').find('@') > -1):
			# e-mail
			if(self.request.get('data').replace('\n','').replace(' ','').replace('	','') == ''):
				# no data recorded
				finished_text = "CrowdBot ran your sketch, '" + cgi.escape(sketch.programname).replace('@','').replace('#','').replace('/','') + """'.

No data was returned by your sketch. Use the Serial functions to report data from CrowdBot's Arduino."""
			else:
				# send data record
				finished_text = "CrowdBot ran your sketch, '" + cgi.escape(sketch.programname).replace('@','').replace('#','').replace('/','') + """'.

Data returned by your sketch is stored at http://mapmeld.com/crowdbot/out?get=feed&id=""" + self.request.get('id')
			mail.send_mail(sender=crowdbotconfig.mail,
              to=self.request.get('mail'),
              subject="CrowdBot ran your sketch",
              body=finished_text)

	else:
		# accept a new sketch from the form
		sketch = CrowdBotProgram()
		sketch.programname = self.request.get('sketchname')
		sketch.username = self.request.get('identify')
		sketch.programtext = db.Text(self.request.get('mysketch'))
		sketch.dostream = self.request.get('dostream')
		sketch.dosend = self.request.get('dosend')
		sketch.hasRun = 'False'
		sketch.put()
		self.redirect('/crowdbot?screen=watch')

# API requests
class CrowdBotOut(webapp.RequestHandler):
  def get(self):
	if(self.request.get('get') == 'livecode'):
		# token = channel.create_channel('crowdbot')
		# print out a mini-page about the current program, which refreshes every few minutes by default or by Channel API
		livesketch = CrowdBotProgram().gql("WHERE hasRun = 'True' ORDER BY uploaded DESC").get()
		sketchtitle = ""
		if(livesketch is not None):
			sketchtitle = cgi.escape( livesketch.programname )
		self.response.out.write('''<!DOCTYPE html>
<html>
	<head>
		<meta http-equiv="refresh" content="60"/>
		<title>Current CrowdBot Program</title>
		<script type="text/javascript" src="/shCore.js"></script>
		<script type="text/javascript" src="/shBrushCpp.js"></script>
		<link rel='stylesheet' type='text/css' href='/shCore.css'/>
		<link rel='stylesheet' type='text/css' href='/shThemeDefault.css'/>
	</head>
	<body>
		<span id="codetitle" style="font-family:courier;">''' + sketchtitle + '''</span>
		<input type="button" value="Refresh" onclick="window.location.reload()"/>
		<hr/>
		<pre class="brush: cpp">\n''')
		# find the last sketch to be downloaded to the board - print program name and source code
		if(livesketch is not None):
			#self.response.out.write(cgi.escape(livesketch.programname) + '<hr/>')
			#self.response.out.write(cgi.escape(livesketch.programtext.replace('\n','<br/>')).replace('&lt;br/&gt;','<br/>').replace(' ','&nbsp;'))
			self.response.out.write(cgi.escape(livesketch.programtext))
		else:
			self.response.out.write('No program loaded\n')
		self.response.out.write('''		</pre>
		<script type="text/javascript">
			SyntaxHighlighter.all()
		</script>
	</body>
</html>''')
	elif(self.request.get('get') == 'livedata'):
		# display any data relayed by the CrowdBot host		
		if(1 == 0):
		#try:
			token = channel.create_channel('crowdbot_data')
			self.response.out.write('''<!DOCTYPE html>
<html>
	<head>
		<title>CrowdBot Data Stream</title>
		<script type="text/javascript" src="/_ah/channel/jsapi"></script>
		<script type="text/javascript">
function init(){
	channel = new goog.appengine.Channel("''' + token + '''");
	socket = channel.open();
	socket.onmessage = function(msg){
		if(msg.data == "CLEAR-DATA"){
			while($("datadiv").childNodes.length >= 1){
				$("datadiv").removeChild($("datadiv").firstChild);       
			}
			var dataline = document.createElement('p');
			dataline.innerHTML = "Awaiting data...";
			$("datadiv").appendChild(dataline);
		}
		else{
			var dataline = document.createElement('p');
			dataline.innerHTML = msg.data;
			$("datadiv").appendChild(dataline);
			window.scrollBy(0,50);
		}
	};
}
function $(id){
	return document.getElementById(id);
}
		</script>
		<style type="text/css">
html, body{
	font-family: courier;
}
		</style>
	</head>
	<body onload="init()">
		<div id="datadiv">
			<p>Awaiting data...</p>
		</div>
	</body>
</html>''')
		#except:
		else:
			# over channel connection limit (100 connections in 24 hours)
			# show feed of last program to send data
			lastread = CrowdBotProgram().gql("WHERE hasRun = 'Complete' ORDER BY uploaded DESC")
			found = 0
			for program in lastread:
				if(program.feed is not None):
					if(len(str(program.feed)) > 3):
						found = 1
						self.redirect('/crowdbot/out?get=feed&id=' + str(program.key().id()))
						break
			if(found == 0):
				self.response.out.write('Over channel limit and no archived data')

	elif(self.request.get('get') == 'current'):
		# send the current program to the function given by jsonp 
		self.response.out.write(cgi.escape(self.request.get('jsonp')) + '("')
		livesketch = CrowdBotProgram().gql("WHERE hasRun = 'True' ORDER BY uploaded DESC").get()
		if(livesketch is not None):
			self.response.out.write(livesketch.programtext.replace('"','\\"').replace('\r','|~|').replace('\n','|~|'))
		self.response.out.write('")')
	elif(self.request.get('get') == 'feed'):
		sketch = CrowdBotProgram.get_by_id(long(self.request.get('id')))
		self.response.out.write(cgi.escape(sketch.feed.replace('\n','<br/>')).replace('&lt;br/&gt;','<br/>').replace(' ','&nbsp;'))
	else:
		# output the earliest-submitted pending sketch ( will be updated to include more information about user, sketch name )
		sketch = CrowdBotProgram().gql("WHERE hasRun = 'False' ORDER BY uploaded ASC").get()
		livesketch = CrowdBotProgram().gql("WHERE hasRun = 'True' ORDER BY uploaded DESC").get()
		if(sketch is not None):
			# write metadata about sketch
			self.response.out.write(str(sketch.key().id()) + "|")
			self.response.out.write(sketch.username.replace('|','-') + "|")
			if(sketch.dosend == 'on'):
				self.response.out.write("TRUE|")
			else:
				self.response.out.write("FALSE|")
			if(sketch.dostream == 'on'):
				self.response.out.write("TRUE|")
			else:
				self.response.out.write("FALSE|")
			# write sketch
			self.response.out.write(sketch.programtext)

			# move pending sketch to live
			sketch.hasRun = 'True'
			sketch.put()
			if(livesketch is not None):
				# move live sketch to 'Complete'
				livesketch.hasRun = 'Complete'
				livesketch.put()
			
			# use Channel API to update live code and data views
			#channel.send_message('crowdbot', cgi.escape(sketch.programname) + '<hr/>' + cgi.escape(sketch.programtext))
			channel.send_message('crowdbot_data', 'CLEAR-DATA')

			# send Tweets to authors of latest and next sketch, if Twitter was provided
			# based on Anil Shanbhag's Twitter Bot: http://anilattech.wordpress.com/2011/10/29/making-a-twitter-bot-using-appengine/
			if(sketch.username.find('@') == 0):

				starting_format = "%s: your sketch '%s' will run on #CrowdBot for the next 2+ minutes"

				# oauth client released by Mike Knapp (see twitteroauth.py for more information)
				client = twitteroauth.TwitterClient(crowdbotconfig.consumer_key, crowdbotconfig.consumer_secret, crowdbotconfig.callback_url)

				additional_params = {
					"status": starting_format % (sketch.username, sketch.programname.replace('@','').replace('#','').replace('/',''))
				}
				result = client.make_request(
					"http://twitter.com/statuses/update.json",
					token=crowdbotconfig.access_token,
					secret=crowdbotconfig.access_token_secret,
					additional_params=additional_params,
					method=POST)
				logging.info(result.content)
		else:
			# there are no pending programs
			self.response.out.write('no new program')

# data model for user-submitted sketches
class CrowdBotProgram(db.Model):
	programname = db.StringProperty(multiline=False)
	username = db.StringProperty(multiline=False)
	programtext = db.TextProperty()
	dosend = db.StringProperty(multiline=False)
	dostream = db.StringProperty(multiline=False)
	hasRun = db.StringProperty(multiline=False)
	uploaded = db.DateTimeProperty(auto_now=True)
	feed = db.TextProperty()

# webapp framework within AppEngine
application = webapp.WSGIApplication([('/crowdbot/out',CrowdBotOut),
									('/crowdbot.*',CrowdBotIn)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()