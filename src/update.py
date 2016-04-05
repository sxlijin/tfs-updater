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


import csv, locale, time, shutil, inspect
import src.logger
import lib.requests as requests


logger = runtime = log = None # to be init'd by initialize()
rsn_list = []
rsn_dict = {}


def initialize():
    """Initialize the globals."""
    global logger, runtime, log
    logger, runtime = src.logger.get_new_logger()
    log = logger.log


def terminate(err):
    """
    Terminate with sys.exit(1) and record it in the log as a fatal error.
    """
    log('FATAL ERROR ENCOUNTERED (details below)')
    log(err)
    sys.exit(err)


def set_gdoc_url_key(specified_gdoc_key):
    """
    Set global $gdoc_url_key so every method knows what to request from.
    """
    if specified_gdoc_key == None: 
        terminate('received GDoc key "%s"' % specified_gdoc_key)

    global gdoc_url_key
    gdoc_url_key = specified_gdoc_key
    log('Setting gdoc_url_key to %s' % gdoc_url_key)
    return gdoc_url_key



def request_memberlist():
    """
    Requests the list of TFS members to update hiscores for, specifically from 
    the Google Sheet "TFS Hiscores - Data/db-memberlist".

    Parses list into $rsn_list global and returns it.
    """
    log('Retrieving memberlist...')
    gdoc_url_base   = 'https://docs.google.com/spreadsheet/pub?output=csv&key='
    gdoc_url = gdoc_url_base + gdoc_url_key + '&output=csv#gid=62'
    log('Attempting to retrieve memberlist from %s' % gdoc_url)
    gdoc_response = requests.get(gdoc_url)
    gdoc_contents = gdoc_response.content
    
    if gdoc_response.status_code != 200:
        terminate('Received status code %d on memberlist retrieval.'
                    % gdoc_response.status_code)

    log('Memberlist successfully retrieved')
    global rsn_list ## Must include global declaration to modify it
    rsn_list = [rsn for rsn in gdoc_contents.splitlines() if len(rsn) > 0]
    ## Ignore blank entries; we know there is at least one because the first
    ## entry should always be blank because the GDoc needs a blank header to
    ## to sort (alphabetize) the memberlist.

    return rsn_list


def request_hiscores_for(rsn):
    """
    Downloads the lite hiscores for $rsn, calls the parser on the data, and
    finishes by writing to the $rsn_dict global.
    """
    log('Requesting hiscores for %s' % rsn)
    hs_url = 'http://hiscore.runescape.com/index_lite.ws?player=%s' % rsn
    requested_data = requests.get(hs_url)
    
    ## if data request was successful
    if requested_data.status_code == 200:
        global rsn_dict
        rsn_dict[rsn] = parse_hs_data(requested_data.content)
    
    ## otherwise report failure and the received response code
    else:
        f = (rsn, requested_data.status_code)
        log('    Excluding %s: %d response code on hiscore retrieval' % f)


def parse_hs_data(received_content):
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


def request_all_hiscores():
    """
    Calls request_hiscores_for() for every name in the $rsn_list global
    """
    try: 
        for rsn in rsn_list:    request_hiscores_for(rsn)
    except requests.exceptions.RequestException as e:
        log('Something just went REALLY wrong; no idea what. Details below.')
        terminate(e)


## writecsv(dict, .csv): dict, String -> None
## Writes contents of $hashtable to $out_csv as a .csv file.
def write_csv(hashtable, out_csv):
    update_writer = csv.writer( open(out_csv,'w'), 
                                delimiter=',', 
                                lineterminator='\n', 
                                quotechar ='"' )
    ## Initializes the csv.writer(); cannot use dialect='excel'
    ## because running in Windows then automatically sets lineterminator to '\r\n'
    for key in hashtable : 
        row = [runtime, key, ''] + hashtable[key]
        log('|'.join((repr(datum) for datum in row)))
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
## Archives updated-hiscores.csv in log/ for future reference.
def archive():
    try :
        shutil.copy('updated-hiscores.csv',
                    'log/updated-hiscores_{timestamp}.csv'.format(
                        timestamp=runtime)
                    )
    except IOError as error: 
        log('IOError encountered; could not archive %s (action:cp)'
                % error.filename)
 

## auto_update(): none -> none
## Calls everything in order.
def auto_update(gdoc_key=None):
    initialize()
    log('Beginning automatic update process')

    log('Runtime was set to: %s' % logger.runtime)

    log('Setting the GDoc URL key')
    set_gdoc_url_key(gdoc_key)

    log('Retrieving memberlist...')
    request_memberlist()

    log('Requesting and parsing hiscores for all members...')
    request_all_hiscores() ## Download everything

    log('Writing parsed hiscores to updated-hiscores.csv...')
    write_csv(rsn_dict, 'updated-hiscores.csv')

    log('Archiving updated-hiscores.csv for future reference.')
    archive()

    log('Finishing automatic update process.')


if __name__ == '__main__':
    auto_update()
    # main() has finished executing - exiting now.
    sys.exit(0)
