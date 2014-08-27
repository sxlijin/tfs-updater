#! /usr/bin/python

import subprocess
from sys import platform

exe = './src/autoupdate.sh' ## Default
if platform == 'win32': exe = r'src\autoupdate.bat'
elif platform in ('linux2','darwin'): exe = './src/autoupdate.sh'
else:
  print 'Your operating system was not recognized. Defaulting to autoupdate.sh.'
  print 'Please run update.py (in bin) with the --auto switch to update the hiscores instead.'

print 'Please wait... running the updater.'
print 'You can find the update log in update_log.txt.'
print '  The log for the most recent update will be at the end of update_log.txt.'

subprocess.call(exe)

#p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#out, err = p.communicate()
#print out
