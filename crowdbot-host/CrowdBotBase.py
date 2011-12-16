# CrowdBotBase.py
# This program runs on the host computer connected to the Arduino
# It checks for pending sketches on the CrowdBot server, and uploads them to the board

import time, urllib, os

loops = 0
# while loops < 144: # 144 loops x 10 minutes = 24 hours
while loops < 125:
	program = urllib.urlopen('http://mapmeld.appspot.com/crowdbot/out').read()
	if(program != 'no new program'):
		#print program
		myfilename = 'runitnow'
		saveprogram = open('C:/Users/ndoiron/Documents/Arduino/' + myfilename + '.pde','w')
		saveprogram.write(program)
		saveprogram.close()
		os.chdir('C:/Users/ndoiron/Documents/Arduino/')
		print os.system('abuild.bat -v -u ' + myfilename + '.pde')
		time.sleep(200)
	else:
		print "no new program"
		time.sleep(60)  # 1 minute
	loops = loops + 1
