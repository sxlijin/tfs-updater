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
CSV_OUT = 'UPLOAD ME TO TFS HISCORES (using Replace current sheet on db-main).csv'
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


def parse_hs_data(received_data):
    """
    Returns a list containing the data appropriately ordered for the GSheet.

    Parses the <requests>.content received from a successful hiscore request,
    which will look something like the example below.

        '477834,1536,183222987\n402950,80,2181102\n306123,86,3613689\n
        311318,90,5487764\n197949,99,13892341\n99545,99,16003196\n408384,66,
        525159\n79445,99,18005632\n202257,96,9708671\n247276,89,5234718\n-1,1,
        -1\n111310,99,13054112\n76514,99,13967725\n82595,99,13035060\n86307,99,
        13039131\n112240,92,6951868\n-1,1,-1\n-1,1,-1\n-1,1,-1\n-1,1,-1\n-1,1,
        -1\n146607,82,2504944\n-1,1,-1\n-1,1,-1\n-1,1,-1\n39137,111,46013995\n
        -1,1,-1\n-1,0,-1\n-1,-1\n-1,-1\n-1,-1\n-1,-1\n-1,-1\n-1,-1\n-1,-1\n-1,
        -1\n-1,-1\n-1,-1\n-1,-1\n-1,-1\n647,24824\n49449,280\n-1,-1\n-1,-1\n-1,
        -1\n-1,-1\n-1,-1\n-1,-1\n-1,-1\n51277,44\n-1,-1\n-1,-1'

    Info from http://services.runescape.com/m=rswiki/en/Hiscores_APIs

    Format is the following repeated: '<rank>,<level>,<experience> '
    """
    received_order = ( ['Total level'] + 
                       ['Attack', 'Defence', 'Strength', 'Constitution', 
                        'Ranged', 'Prayer', 'Magic', 'Cooking', 'Woodcutting', 
                        'Fletching', 'Fishing', 'Firemaking', 'Crafting', 
                        'Smithing', 'Mining', 'Herblore', 'Agility', 'Thieving', 
                        'Slayer', 'Farming', 'Runecrafting', 'Hunter', 
                        'Construction', 'Summoning', 'Dungeoneering', 
                        'Divination'] + 
                       ['Bounty Hunter', 'B.H. Rogues', 'Dominion Tower', 
                        'The Crucible', 'Castle Wars games', 'B.A. Attackers', 
                        'B.A. Defenders', 'B.A. Collectors', 'B.A. Healers', 
                        'Duel Tournament', 'Mobilising Armies', 'Conquest', 
                        'Fist of Guthix', 'GG: Athletics', 'GG: Resource Race', 
                        'WE2: Armadyl lifetime contribution', 
                        'WE2: Bandos lifetime contribution', 
                        'WE2: Armadyl PvP kills', 'WE2: Bandos PvP kills', 
                        'Robbers caught during Heist', 
                        'loot stolen during Heist', 'CFP: 5 game average', 
                        'AF15: Cow Tipping',
                        'AF15: Rats killed after the miniquest.'])

    # isolate relevant f2p hiscores, discarding ranks from the data
    f2p_hiscores_array = {  datum_type:datum.split(',')[1:] 
                            for datum, datum_type
                            in zip(received_data.split(), received_order)
                            }

    
    # reorder entries as appropriate
    ordered = [ 'Attack', 'Strength', 'Defence', 'Constitution', 'Ranged',
                'Magic', 'Prayer', 'Runecrafting', 'Crafting', 'Mining',
                'Smithing', 'Woodcutting', 'Firemaking', 'Fishing', 'Cooking',
                'Dungeoneering', 'Fist of Guthix'
                ]
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
    log('Writing parsed data to %s' % out_csv)
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
## Archives csv in log/ for future reference.
def archive():
    try :
        shutil.copy(CSV_OUT,
                    'log/hiscores_{timestamp}.csv'.format(
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

    log('Writing parsed hiscores to csv...')
    write_csv(rsn_dict, CSV_OUT)

    log('Archiving updated-hiscores.csv for future reference.')
    archive()

    log('Finishing automatic update process.')


if __name__ == '__main__':
    auto_update()
    # main() has finished executing - exiting now.
    sys.exit(0)
