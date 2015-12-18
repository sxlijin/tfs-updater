#! /usr/bin/python

## This file is part of TFS HISCORES UPDATER.
##
##   TFS HISCORES UPDATER is free software: you can redistribute it and/or 
##   modify it under the terms of the GNU General Public License as published
##   by the Free Software Foundation, either version 3 of the License, or (at 
##   your option) any later version.
##
##   TFS HISCORES UPDATER is distributed in the hope that it will be useful,
##   but WITHOUT ANY WARRANTY; without even the implied warranty of 
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General 
##   Public License for more details.
##
##   You should have received a copy of the GNU General Public License
##   along with TFS HISCORES UPDATER. If not, see http://www.gnu.org/licenses/.

import subprocess
from time import sleep
from sys import platform

exe = './src/autoupdate.sh' ## Default
if platform == 'win32': exe = r'src\autoupdate.bat'
elif platform in ('linux2','darwin'): exe = './src/autoupdate.sh'
else:
  print 'Your operating system was not recognized. Defaulting to autoupdate.sh.'
  print 'Please run update.py (in src) to update the hiscores instead.'

print 'Please wait... calling the updater.'
print 'You can find the update log in update_log.txt.'
print '  The log for the most recent update will be at the end of update_log.txt.'

sleep(5) #Give user time to read this.

subprocess.call(exe)