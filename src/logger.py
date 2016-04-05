#! /usr/bin/env python

## Copyright (c) 2016 Aging Miser

## This file is part of TFS HISCORES UPDATER.
##
##   TFS HISCORES UPDATER is free software: you can redistribute it and/or 
##   modify it under the terms of the GNU General Public License as published
##   by the Free Software Foundation, either version 3 of the License, or (at 
##   your option) any later version.
##
##   TFS HISCORES UPDATER is distributed in the hope that it will be useful,
##   but WITHOUT ANY WARRANTY; without even the implied warranty of 
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the GNU General 
##   Public License for more details.
##
##   You should have received a copy of the GNU General Public License
##   along with TFS HISCORES UPDATER. If not, see http://www.gnu.org/licenses/.

import time, inspect

class Log:
    """
    Generates a timestamped log file in log/ and writes to it.
    """

    def __init__(self):
        """Initialize logger object."""
        self.runtime = get_current_time()
        self.log_fname = 'log/update-log_{timestamp}.log'.format(
                            timestamp=self.runtime)
        self.log('Runtime set to %s' % self.runtime)
        self.log('Setting log file to %s' % self.log_fname)


    def log(self, text):
        """Log the caller function and the message to be logged."""
        # inspect.getouterframes() ->
        # Each record contains a frame object, filename, line number, function
        # name, a list of lines of context, and index within the context.
        UP_ONE_LEVEL = 1
        (_, _, _, caller, _, _) = inspect.getouterframes(
                                    inspect.currentframe(), 2
                                    )[UP_ONE_LEVEL]

        with open(self.log_fname, 'a') as log_obj:
            log_obj.write(u'%20s: ' % caller[:20])
            log_obj.write(unicode(text))
            log_obj.write(u'\n')


def get_current_time():
    """
    Return string representing the current GMT time, yyyy-mm-dd-hh-mm-ss.
    """
    return '-'.join([str(elem).zfill(2) for elem in time.gmtime()[:6]])


def get_new_logger():
    """Return a new logger object and the time at which it was created."""
    logger = Log()
    return (logger, logger.runtime)
