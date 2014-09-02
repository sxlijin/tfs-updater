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
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General 
##   Public License for more details.
##
##   You should have received a copy of the GNU General Public License
##   along with TFS HISCORES UPDATER. If not, see http://www.gnu.org/licenses/.


## CHANGE THIS LINE IF THE GDOC FOR THE HISCORES IS CHANGED
gdoc_url_key = '0Arkz2dsnDdvVdG1DLWU4NDNwSndoS0FCb1hIekw1a2c'
## CHANGE THIS LINE IF THE GDOC FOR THE HISCORES IS CHANGED

runtime = 'yyyy-mm-dd-hh-mm-ss'
rsn_list = []
rsn_dict = {}

import csv, locale, time, shutil, requests
## csv used to generate the .csv
## locale used by dformat()
## 


## set_runtime(): none -> none
## Sets the $runtime global to the time that set_runtime() is called.
def set_runtime():
  global runtime ## Must include global declaration to modify it
  runtime = '-'.join([str(elem).zfill(2) for elem in time.gmtime()[:6]])

## request_memberlist(): none -> none
## Requests db-memberlist and reads its contents into the $rsn_list global
def request_memberlist():
  print 'entering read_memberlist():'
  gdoc_url_base  = 'https://docs.google.com/spreadsheet/pub?output=csv&key='
  gdoc_url = gdoc_url_base + gdoc_url_key + '&output=csv#gid=62'
  gdoc_response = requests.get(gdoc_url)
  gdoc_contents = gdoc_response.content
  global rsn_list ## Must include global declaration to modify it
  rsn_list = gdoc_contents.split('\n') ## CSV has been read in as a string
  while '' in rsn_list:  rsn_list.remove('') ## Remove all blank entries
  ## The first entry should always be blank because the GDoc needs a blank header
  ## to sort (alphabetize) the memberlist.

## request_hiscores_for(rsn): String -> none
## Downloads the lite hiscores for $rsn, calls the parser, writes it to the $rsn_dict global.
def request_hiscores_for(rsn):
  print '  Requesting hiscores for '+rsn+' using request_hiscores_for()'
  hs_url_base = 'http://hiscore.runescape.com/index_lite.ws?player=' ## ??? ADD THIS
  hs_url_key = rsn
  hs_url = hs_url_base + hs_url_key
  
  global rsn_dict
  requested_hiscores_for = requests.get(hs_url)
  if '404 - Page not found' not in requested_hiscores_for.content:
    rsn_dict[rsn] = parse_received_content(requested_hiscores_for.content)
  else:
    print '    Excluding '+rsn+': 404 error returned upon requesting hiscores'


## parse_received_content(received_content): String -> none
## Chews up the lite hiscores and spits out the appropriate format for the TFS hiscores.
def parse_received_content(received_content):
  hiscores_array = [item.split(',')[1:] for item in received_content.split('\n')]
  f2p_hiscores_array = hiscores_array[1:10]+hiscores_array[11:][:5]+hiscores_array[21:][:1]+hiscores_array[25:][:1]+hiscores_array[39:][:1]
  a = f2p_hiscores_array
  ordered = a[0]+a[2]+a[1]+a[3]+a[4]+a[6]+a[5]+a[14]+a[11]+a[13]+a[12]+a[8]+a[10]+a[9]+a[7]+a[15]+a[16]
  ordered_f2p_hiscores_array = [dformat(item) if item != '-1' else '0' for item in ordered] 
  if ordered_f2p_hiscores_array[6] == '1':  ordered_f2p_hiscores_array[6:8]=['10','1,154']
  return ordered_f2p_hiscores_array


## wget_all(): none -> none
## Calls request_hiscores_for() for every name in the $rsn_list global
def request_all_hiscores():
  try: 
    for rsn in rsn_list:  request_hiscores_for(rsn)
  except requests.exceptions.RequestException as e:
    print 'sth spontaneously combusted, but i have no idea what; all i know is:'
    print e


## writecsv(dict, .csv): dict, String -> None
## Writes contents of $hashtable to $out_csv as a .csv file.
def write_csv(hashtable, out_csv):
  update_writer = csv.writer(open(out_csv,'w'), delimiter=',', lineterminator='\n', quotechar ='"')
  ## Initializes the csv.writer(); cannot use dialect='excel'
  ## because running in Windows then automatically sets lineterminator to '\r\n'
  for key in hashtable : update_writer.writerow([runtime, key, ''] + hashtable[key])
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
def archive():
  try :
    shutil.copy('updated-hiscores.csv','csv_archive/hiscores_{timestamp}.csv'.format(timestamp=runtime))
  except IOError as error: 'IOError: could not archive {f} (action:cp)'.format(f=error.filename)
 

## auto_update(): none -> none
## Calls everything in order.
def auto_update():
  print 'Initializing auto_update()'
  set_runtime()
  print 'Setting runtime to: '+runtime
  print 'Calling request_memberlist() from auto_update()'
  request_memberlist()
  print 'Calling request_all_hiscores() from auto_update()'
  request_all_hiscores() ## Download everything
  print 'Calling write_csv() from auto_update()'
  write_csv(rsn_dict,'updated-hiscores.csv')
  print 'Calling archive() from auto_update()'
  archive()
  print 'Exiting auto_update()'

def main():
  auto_update()
  print 'main() has finished executing - exiting now.'


if __name__ == '__main__': main()

