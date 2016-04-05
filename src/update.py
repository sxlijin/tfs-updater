#! /usr/bin/python

## Copyright (c) 2014 Aging Miser

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



## CHANGE THIS LINE IF THE GDOC FOR THE HISCORES IS CHANGED
gdoc_url_key = '0Arkz2dsnDdvVdG1DLWU4NDNwSndoS0FCb1hIekw1a2c'
## CHANGE THIS LINE IF THE GDOC FOR THE HISCORES IS CHANGED



runtime = 'yyyy-mm-dd-hh-mm-ss'
f_out_log = ''
rsn_list = []
rsn_dict = {}

import csv, locale, time, shutil
import lib.requests as requests
## csv used to generate the .csv
## locale used by dformat()


class Log:
    """
    Generates a timestamped log file in log/ and writes to it.
    """

    def __init__(self):
        if runtime == 'yyyy-mm-dd-hh-mm-ss': 
            set_runtime()

        self.log_fname = open('log/update-log-%s.log' % runtime, 'w')

    def write(self, text):
        self.log_fname.write(unicode(text))
        self.log_fname.write(u'\n')

    def close(self):
        self.log_fname.close()


def set_runtime():
    """
    Generate string representing the current GMT time, yyyy-mm-dd-hh-mm-ss.
    Writes said string to the $runtime global and returns it.
    """
    global runtime
    if runtime != 'yyyy-mm-dd-hh-mm-ss': return runtime
    runtime = '-'.join([str(elem).zfill(2) for elem in time.gmtime()[:6]])
    return runtime



def request_memberlist(logger):
    """
    Requests the list of TFS members to update hiscores for, specifically from 
    the Google Sheet "TFS Hiscores - Data/db-memberlist".

    Parses list into $rsn_list global and returns it.
    """
    logger.write('entering read_memberlist():')
    gdoc_url_base   = 'https://docs.google.com/spreadsheet/pub?output=csv&key='
    gdoc_url = gdoc_url_base + gdoc_url_key + '&output=csv#gid=62'
    gdoc_response = requests.get(gdoc_url)
    gdoc_contents = gdoc_response.content

    global rsn_list ## Must include global declaration to modify it
    rsn_list = [rsn for rsn in gdoc_contents.splitlines() if len(rsn) > 0]
    ## Ignore blank entries; we know there is at least one because the first
    ## entry should always be blank because the GDoc needs a blank header to
    ## to sort (alphabetize) the memberlist.

    return rsn_list


def request_hiscores_for(logger, rsn):
    """
    Downloads the lite hiscores for $rsn, calls the parser on the data, and
    finishes by writing to the $rsn_dict global.
    """
    logger.write(' Requesting hiscores for %s using request_hiscores_for()' % rsn)
    hs_url = 'http://hiscore.runescape.com/index_lite.ws?player=%s' % rsn
    requested_data = requests.get(hs_url)
    
    ## if data request was successful
    if requested_data.status_code == 200:
        global rsn_dict
        rsn_dict[rsn] = parse_received_content(logger, requested_data.content)
    
    ## otherwise report failure and the received response code
    else:
        f = (rsn, requested_data.status_code)
        logger.write('     Excluding %s: %d response code on hs request' % f)


def parse_received_content(logger, received_content):
    """
    Returns a list containing the data appropriately ordered for the GSheet.

    Parses the <requests>.content received from a successful hiscore request,
    which will look something like the example below.

        '465511,1535,183078301\n393375,80,2180227\n297382,86,3606468\n303931,
        90,5479557\n190674,99,13880142\n93868,99,15982524\n400308,66,503772\n
        73304,99,17998984\n197868,96,9703486\n242848,89,5206653\n-1,1,-1\n
        106229,99,13049112\n72673,99,13967245\n77291,99,13034450\n78483,99,
        13038635\n106483,92,6951638\n-1,1,-1\n-1,1,-1\n-1,1,-1\n-1,1,-1\n-1,1,
        -1\n141871,82,2504444\n-1,1,-1\n-1,1,-1\n-1,1,-1\n37265,111,45987084\n
        -1,1,-1\n-1,-1\n-1,-1\n-1,-1\n-1,-1\n-1,-1\n-1,-1\n-1,-1\n-1,-1\n-1,
        -1\n-1,-1\n-1,-1\n-1,-1\n650,24824\n50365,280\n-1,-1\n-1,-1\n-1,-1\n
        -1,-1\n-1,-1\n-1,-1\n-1,-1\n48936,44\n-1,-1\n-1,-1\n'

    Format is the following repeated: '<rank>,<level>,<experience>\n'
    """
    # discard ranks from the data, split into one list per hiscore (eg lv, xp)
    hiscores_array = [  item.split(',')[1:] 
                        for item in received_content.split('\n')]

    # isolate relevant f2p hiscores
    f2p_hiscores_array = ( hiscores_array[1:10]
                            + hiscores_array[11:][:5]
                            + hiscores_array[21:][:1]
                            + hiscores_array[25:][:1]
                            + hiscores_array[39:][:1] )
    
    # reorder entries as appropriate
    ordered = [0, 2, 1, 3, 4, 6, 5, 14, 11, 13, 12, 8, 10, 9, 7, 15, 16]
    ordered = [f2p_hiscores_array[i] for i in ordered]

    # concatenate 
    ordered = [dformat(item) if item != '-1' else '0' for item in sum(ordered, [])] 

    # if constitution not high enough to appear on hs, set to 10
    if ordered[6] == '1':    ordered[6:8]=['10','1,154']
    return ordered


def request_all_hiscores(logger):
    """
    Calls request_hiscores_for() for every name in the $rsn_list global
    """
    try: 
        for rsn in rsn_list:    request_hiscores_for(logger, rsn)
    except requests.exceptions.RequestException as e:
        logger.write('sth spontaneously combusted, but i have no idea what; all i know is:')
        logger.write(e)


## writecsv(dict, .csv): dict, String -> None
## Writes contents of $hashtable to $out_csv as a .csv file.
def write_csv(logger, hashtable, out_csv):
    update_writer = csv.writer( open(out_csv,'w'), 
                                delimiter=',', 
                                lineterminator='\n', 
                                quotechar ='"' )
    ## Initializes the csv.writer(); cannot use dialect='excel'
    ## because running in Windows then automatically sets lineterminator to '\r\n'
    for key in hashtable : 
        row = [runtime, key, ''] + hashtable[key]
        logger.write(row)
        update_writer.writerow(row)

    ## In the old version, the update form automatically timestamped each update request
    ## and the script would include these timestamps in the final version so that people
    ## would be able to see when they had last updated their stats; the third column was
    ## also left blank for unknown reasons (a placeholder perhaps? - or maybe there was
    ## functionality intended for it). As a result, the db-main (which contains all the
    ## raw data) is formatted like so:
    ## <time of update> <RSN> <blank> <hiscores[0]> <hiscores[1]> ...


## dform(numstring) -> string
## Formats a numerical string per American decimal notation; that is, commas mark off every 10^3.
def dformat(num):
    locale.setlocale(locale.LC_ALL,'')
    return locale.format('%d', int(num), True)


## archive() -> None
## Logs updated-hiscores.csv in csv_archive/ for future reference.
def archive(logger):
    try :
        shutil.copy('updated-hiscores.csv','csv_archive/hiscores_{timestamp}.csv'.format(timestamp=runtime))
    except IOError as error: 
        logger.write('IOError: could not archive %s (action:cp)' % error.filename)
 

## auto_update(): none -> none
## Calls everything in order.
def auto_update():
    logger = Log()

    logger.write('Initializing auto_update()')

    logger.write('Setting runtime to: %s' % set_runtime())
    logger.write('Calling request_memberlist() from auto_update()')
    request_memberlist(logger)

    logger.write('Calling request_all_hiscores() from auto_update()')
    request_all_hiscores(logger) ## Download everything

    logger.write('Calling write_csv() from auto_update()')
    write_csv(logger, rsn_dict, 'updated-hiscores.csv')

    logger.write('Calling archive() from auto_update()')
    archive(logger)

    logger.write('Exiting auto_update()')


if __name__ == '__main__':
    auto_update()
    # main() has finished executing - exiting now.
    sys.exit(0)
