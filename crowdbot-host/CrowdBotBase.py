# CrowdBotBase.py
# This program runs on the computer connected to the Arduino
# It checks for pending sketches on the CrowdBot server

import time, urllib, os

loops = 0
# while loops < 144: # 144 loops x 10 minutes = 24 hours
while loops < 1:
    program = urllib.urlopen('http://mapmeld.appspot.com/crowdbot/out').read()
    #print program
    myfilename = 'runitnow'
    saveprogram = open('C:/Users/Doiron/arduino-0022/' + myfilename + '.pde','w')
    saveprogram.write(program)
    saveprogram.close()
    print os.chdir('C:/Users/Doiron/arduino-0022/')
    print os.system('abuild.bat -v -u ' + myfilename + '.pde')
    
    #time.sleep(600)  # 10 minutes
    loops = loops + 1
