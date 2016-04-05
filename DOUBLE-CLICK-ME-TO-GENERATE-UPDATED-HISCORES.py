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



## CHANGE THIS LINE IF THE GDOC FOR THE HISCORES IS CHANGED
gdoc_url_key = '0Arkz2dsnDdvVdG1DLWU4NDNwSndoS0FCb1hIekw1a2c'
## CHANGE THIS LINE IF THE GDOC FOR THE HISCORES IS CHANGED



##  Do NOT modify anything below this line. It will have disastrous consequences.
import lib, src
import sys, traceback

print 'Please wait... calling the updater.'
print 'The update log will be recorded in the most recent file in log/.'

try:
    src.update.auto_update(gdoc_url_key)
except Exception as e:
    print
    print 'FATAL ERROR DEFCON 5 something something very cryptic'
    print 'Seriously though, something went really, really wrong'
    print 'if you\'re seeing this error message. Aging will want'
    print 'to know what the actual error is; here it is:'

    e_trace = traceback.format_exc(sys.exc_info())
    open('FATAL-ERROR-REPORT.log', 'w').write(repr(e)+'\n')
    open('FATAL-ERROR-REPORT.log', 'a').write(e_trace+'\n')

    print
    print e
    print e_trace
    print
    print 'Nothing to do but give up, I suppose...'
    raw_input('Press any key to exit.')
    sys.exit(1)

raw_input("Finished generating updated-hiscores.csv. Press any key to finish.")
sys.exit(0)
