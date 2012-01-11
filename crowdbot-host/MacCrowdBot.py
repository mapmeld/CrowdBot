# CrowdBotBase.py
# This program runs on the host computer connected to the Arduino
# It checks for pending sketches on the CrowdBot server, and uploads them to the board

# basic functionality libraries
import time, urllib, os
# experimental data livestream
# install PySerial from http://pyserial.sourceforge.net
# also configure serial.Serial line to appropriate Arduino USB port
import datetime, serial

# configure app instance for your installation
appinstance = "http://mapmeld.appspot.com"

loops = 0
# while loops < 125: # 125 loops x 1 minute > 2 hours
while loops < 125:
	program = urllib.urlopen(appinstance + '/crowdbot/out').read()
	if(program != 'no new program'):
		#print program
		
		# retrieve metadata before the program text
		# DATA-ID|EMAIL|SEND TRUE/FALSE|STREAM TRUE/FALSE|SKETCH
		programid = program.split("|")[0]
		contact = program.split("|")[1]
		dosend = program.split("|")[2]
		dostream = program.split("|")[3]
		# remove metadata
		program = program[program.find("|")+1:]
		program = program[program.find("|")+1:]
		program = program[program.find("|")+1:]
		program = program[program.find("|")+1:]
		# fix Serial communication bug by adding an error handler
		# code from http://rowley.zendesk.com/entries/46177-undefined-reference-to-cxa-pure-virtual-error-message
		if((program.find('Serial.begin') > -1) and (program.find('void __cxa_pure_virtual()') == -1)):
			program = program + '\n\nextern "C" void __cxa_pure_virtual(){\n  while (1);\n}'

		# do not run programs which write to EEPROM - these can overwrite or even break the Arduino's memory
		if(program.find('EEPROM') > -1):
			continue

		# create a folder to store the program
		myfilename = 'runitnow'
		if(os.path.exists('/users/ndoiron404/Documents/CrowdBot/' + myfilename) == False):
			os.mkdir('/users/ndoiron404/Documents/CrowdBot/' + myfilename)
		os.chdir('/users/ndoiron404/Documents/CrowdBot')
		os.system('cp SConstruct ' + myfilename + '/')
		saveprogram = open('/users/ndoiron404/Documents/CrowdBot/' + myfilename + '/' + myfilename + '.pde','w')
		program = '#include <WProgram.h>\n' + program
		saveprogram.write(program)
		saveprogram.close()
		os.chdir('/users/ndoiron404/Documents/CrowdBot/' + myfilename)
		response = os.system('scons ARDUINO_PORT=/dev/tty.usbmodemfd121 upload')
		# response could feasibly be checked for compilation / upload errors
		print response
		msstart = datetime.datetime.now()
		#time.sleep(120)
		# see if user has asked to check serial port
		if(dosend == "TRUE" or dostream == "TRUE"):
			# init data archive
			outbox = ""
			# open serial port - configure to your computer!
			ser = serial.Serial('/dev/tty.usbmodemfd121', 9600, timeout=0.5)
			# attempt to read serial while program runs for the next two minutes
			while( (datetime.datetime.now() - msstart).seconds < 120 ):
				line = ser.readline().replace('\r','').replace('\n','')
				#print line
				if(line.replace(' ','').replace('	','') != ""):
					# send streaming data through AppEngine Channels API
					if(dostream == "TRUE"):
						urllib.urlopen(appinstance + '/crowdbot/in',urllib.urlencode({'livedata':line}))
					# save to-send data in the outbox
					if(dosend == "TRUE"):
						outbox = outbox + "\n" + line
					if(line.find('DONE') > -1):
						# command to finish early
						break
			# close serial port
			ser.close()
			if(dosend == "TRUE"):
				# upload the data and either e-mail or Tweet link to it
				if(outbox == ""):
					# apologies but no data
					urllib.urlopen(appinstance + '/crowdbot/in',urllib.urlencode({'mail':contact,'id':programid,'data':""}))
				else:
					# send full data report
					urllib.urlopen(appinstance + '/crowdbot/in',urllib.urlencode({'mail':contact,'id':programid,'data':outbox}))
		else:
			# let program run for two minutes
			time.sleep(120)
	else:
		# wait one minute and try for a new pending program
		print "no new program"
		time.sleep(60)
	loops = loops + 1
