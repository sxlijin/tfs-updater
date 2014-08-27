#! /usr/bin/python

## CHANGE THIS LINE IF THE GDOC FOR THE HISCORES IS CHANGED
gdoc_url_key = '0Arkz2dsnDdvVdG1DLWU4NDNwSndoS0FCb1hIekw1a2c'
## CHANGE THIS LINE IF THE GDOC FOR THE HISCORES IS CHANGED

import sys, re, csv, locale, time, shutil, urllib, inspect
from pprint import pprint
from updater_core_vars import *

###################################################################################################################
## 
## UTILITY (23, 130): diff(), verify()
## HELPER (134, 170): print_error_string(), is_header_entry(), parse_timestamp(), is_old_time()
## FORMATTER (174, 207): rsn_lookup(), strip_format(), dform()
## CONFIG (211, 256): set_runtime(), wget_gdocs(), set_memberlist(), set_prev_update_time()
## UPDATER (260, 282): manual_update(), auto_update()
## FILE I/O (286, 320): writecsv(), archive()
## PARSER (324, 457): csv_to_dict(), csv_to_list(), list_to_dict(), merge_csv_update(), merge_entry_update()
## 
###################################################################################################################


##### BEGIN UTILITY FUNCTIONS #####################################################################

## diff(.csv, .csv) -> None ; prints a diff
## Compares two hiscore CSVs, the first being the old and the second the new (updated one)
## Prints out what was deleted and what was updated
def diff(old_db, new_db):
  (old_dict, new_dict) = (csv_to_dict(old_db), csv_to_dict(new_db))
  (old_keys, new_keys) = (old_dict.keys(), new_dict.keys())
  common_keys = list(set(old_keys) & set(new_keys))
  only_old = list(set(old_keys) - set(common_keys))
  only_new = list(set(new_keys) - set(common_keys))
  
  if len(only_old) != 0 :
    print '\nRemoved the following players:'
    for old in only_old :  print '   '+capitalize(old)
  
  if len(only_new) != 0 :
    print '\nAdded the following players:'
    for new in only_new : print '   '+rsn_lookup(new)
  
  print '\nUpdated entries for the following people:'
  for rsn in common_keys : ## For those people in the old hiscores and the new hiscores
    if old_dict[rsn][:-1] != new_dict[rsn][:-1] : ## If their hiscore entry was updated
      print '   Updated hiscore entries for {player} {now} (previously updated {old})'.format(player=rsn_lookup(rsn), now=new_dict[rsn][-1], old=old_dict[rsn][-1])
     # print old_dict[rsn]
     # print new_dict[rsn]
      
     # for (old_stat, new_stat) in (old_dict[rsn], new_dict[rsn]) :  print ' '*6+'Changed {stat} from {old} to {new}'.format(stat=header[i], old=dform(old_stat), new=dform(new_stat))

     # for i in range(len(header)) :
     #   if old_stat != new_stat : print '      Changed {stat} from {old} to {new}'.format(stat=header[i], old=dform(old_dict[rsn][i]), new=dform(new_dict[rsn][i]))
      
      for i in range((len(header)-1)/2) : ## For every datapoint in the hiscore entry, excluding FoG rating
        ## Effectively maps range(15) to [(0,1),(2,3), ... ,(28,29)]
        (lv_index, xp_index) = (2*i, 2*i+1)
	(old_lv, new_lv, old_xp, new_xp) = (old_dict[rsn][lv_index], new_dict[rsn][lv_index], old_dict[rsn][xp_index], new_dict[rsn][xp_index])
	(old_lv, new_lv, old_xp, new_xp) = (int(old_lv), int(new_lv), int(old_xp), int(new_xp))
        update_string = '      Updated {stat} to {new} from {old}'
	updated = True
        
	if new_lv == old_lv and new_xp == old_xp : 
	  updated = False
        elif new_xp != old_xp :
          update_string = update_string.format(stat=header[xp_index], new=dform(new_xp), old=dform(old_xp))
	  if new_lv == old_lv :  update_string += ' ({level} is {currently})'.format(level=header[lv_index], currently=dform(new_lv))
	  else :  update_string += ' ({stat} updated to {new} from {old})'.format(stat=header[lv_index], new=dform(new_lv), old=dform(old_lv))
        elif new_lv != old_lv and new_xp == old_xp :  ## This case should not be possible because of verify()
          update_string = update_string.format(stat=header[lv_index], new=dform(new_lv), old=dform(old_lv))
	
        if updated :  print update_string
      
      i = len(header) - 1 ## Separate case to handle FoG rating
      if new_dict[rsn][i] != old_dict[rsn][i] :
        print '    Updated {stat} to {new} from {old}'.format(stat=header[i], new=dform(new_dict[rsn][i]), old=dform(old_dict[rsn][i]))


## verify(string, list) -> list
## Takes a list of stats in the form (lvl, exp, lvl, exp, ..., fog rating)
## And verifies that all the lvl and exp numbers are realistic
## If unrealistic numbers are present, it removes that entry and says so
## If the level is below 99 (or 120 in the case of DG) it assumes the level
## is realistic and wipes the xp entry if the xp doesn't correspond
def verify(rsn, update):
  ## clear bad datapoints from the list
  for i in range((len(header)-1)/2) : ## For every datapoint in the hiscore entry, excluding FoG rating and DG
    ## Effectively maps range(15) to [(0,1),(2,3), ... ,(28,29)]
    (lv_index, xp_index) = (2*i, 2*i+1)
    (current_lv, current_xp) = (int(update[lv_index]), int(update[xp_index]))
    next_lv = current_lv + 1
    
    if current_xp > 200000000 : ## Cannot have more than 200M xp in a skill
      print_error_string(rsn, xp_index, current_xp)
      update[xp_index] = 0
    
    if is_header_entry('Dungeoneering', lv_index) : ## If the skill is DG
      if current_lv > 120 :
        ## If above the maximm level
        print_error_string(rsn, lv_index, current_lv)
        update[lv_index] = 0
      elif current_xp < exptable[current_lv] :
        ## If below lower bound on xp
        print_error_string(rsn, xp_index, current_xp)
        update[xp_index] = exptable[current_lv]
      elif (current_lv != 120) and (current_xp >= exptable[next_lv]) :
        ## If at or above upper bound, but only when skill isn't 99
        print_error_string(rsn, xp_index, current_xp)
        update[xp_index] = exptable[current_lv]
    
    else : ## If the skill isn't DG
      if current_lv > 99 :
        ## If above the maximum level
        print_error_string(rsn, lv_index, current_lv)
        update[lv_index] = 0
      elif current_xp < exptable[current_lv] :
        ## If below lower bound on xp
        print_error_string(rsn, xp_index, current_xp)
        update[xp_index] = exptable[current_lv]

      elif (current_lv != 99) and (current_xp >= exptable[next_lv]) :
        ## If at or above upper bound, but only when skill isn't 99
        print_error_string(rsn, xp_index, current_xp)
        update[xp_index] = exptable[current_lv]
    # End for loop
  return update

####### END UTILITY FUNCTIONS #####################################################################



##### BEGIN HELPER FUNCTIONS ######################################################################

## print_error_string(string, int, numstring) -> None ; prints an error string
## RSN is the player's RSN
## i is the header index of the stat to report the error for
## bad_stat_val is the bad value that was given for the stat
def print_error_string(rsn, i, bad_stat_val):
  error_string = 'Bad entry for {player} in {stat} ({badval}) - entry reset.'
  print error_string.format(player=rsn_lookup(rsn), stat=header[i], badval=dform(bad_stat_val))


## is_header_entry(string, int) -> bool
## Returns a boolean reflecting whether or not the entry at header[header_index] contains string
def is_header_entry(string, header_index):  return bool(re.search(string, header[header_index]))

## parse_timestamp(str) -> list
## Converts a GDocs timestamp to a list in the form [yyyy,mm,dd,hh,mm,ss]
def parse_timestamp(raw_timestamp):
  try:
    times = re.search('(\d+)/(\d+)/(\d+) (\d+):(\d+):(\d+)', raw_timestamp).groups()
    times = [ value.zfill(2) for value in times ]
    #print times
  except AttributeError as e:
    return ['0000','00','00','00','00','00']
  else:
    year = times.pop(2)
    return [ year ] + times


## is_old_time(str) -> bool
## Checks if a timestamp is older than last_update
def is_old_time(raw_timestamp):
  timestamp = parse_timestamp(raw_timestamp)
  times = [timestamp, last_update]
  return (last_update == sorted(times)[-1]) and (timestamp != last_update)

####### END HELPER FUNCTIONS ######################################################################



##### BEGIN FORMATTER FUNCTIONS ###################################################################

## rsn_lookup(string, [raiseerror=bool]) -> string
## Returns the corresponding RSN in the memberlist; prints an error if the query fails
def rsn_lookup(rsn_query):
  if type(rsn_query) is not str :
    print 'rsn_lookup() must take a string as argument; was given ' + str(query)
  query = capitalize(rsn_query)
  if strip_format(query) in memberlist :  query = memberlist[strip_format(query)]
    
  return query


## capitalize(string) -> string
## Returns the properly capitalized form of a RSN
def capitalize(string):
  ## DO NOT split on whitespace; RSNs can have multiple consecutive spaces
  return ' '.join( [part.capitalize() for part in str(string).split(' ')] )


## strip_format(string) -> string
## Used to make sure that the same RSN formatted two different ways is recognized as the same RSN
## Converts input to lowercase and replaces all underbars with spaces
def strip_format(formatted_string):  return re.sub('_', ' ', formatted_string.lower())


## dform(numstring) -> string
## Formats a numerical string per American decimal notation; that is, commas mark off every 10^3
def dform(num):
  locale.setlocale(locale.LC_ALL,'')
  return locale.format('%d', int(num), True)

####### END FORMATTER FUNCTIONS ###################################################################



##### BEGIN CONFIG FUNCTIONS ######################################################################

## set_runtime() ->  None ; sets the runtime timestamp of the script
def set_runtime():
  global runtime
  global update_filename
  global db_old_filename
  
  runtime = '-'.join([ str(elem).zfill(2) for elem in time.gmtime()[:6] ])
  update_filename = 'db-update_{timestamp}.csv'.format(timestamp = runtime)
  db_old_filename = 'db-old_{timestamp}.csv'.format(timestamp = runtime)


## wget_gdocs() -> None ; downloads two CSV files from the published Google Doc
def wget_gdocs():
  set_runtime()
  
  gdoc_url_base  = 'https://docs.google.com/spreadsheet/pub?output=csv&key='
  gdoc_url = gdoc_url_base + gdoc_url_key ## Note that gdoc_url_key is a global initialized on line 4
  
  urllib.urlretrieve(gdoc_url+'&gid=41', update_filename) ## Update requests
  urllib.urlretrieve(gdoc_url+'&gid=38', db_old_filename) ## Existing hiscores
  urllib.urlretrieve(gdoc_url+'&gid=62', 'db-memberlist.csv') ## Memberlist


## set_memberlist() -> None ; reads 'db-memberlist' into the global var memberlist
def set_memberlist():
  f = open('db-memberlist.csv','rU')
  global memberlist
  memberlist = {}
  for rsn in f.read().split('\n') :
    if rsn != '' and rsn[0] != '#' :  memberlist[strip_format(rsn)] = rsn


## set_prev_update_time(dict) -> None ; sets global var last_update to the latest timestamp
def set_prev_update_time(hashtable):
  global last_update
  #mm/dd/yyyy hh:mm:ss
  str_timestamps = [ value[-1] for value in hashtable.values() ]
  num_timestamps = []
  for str_time in str_timestamps :
    timestamp = parse_timestamp(str_time)
    if timestamp not in num_timestamps :  num_timestamps.append(timestamp)
    random = str_time
  last_update = sorted(num_timestamps)[-1] 

####### END CONFIG FUNCTIONS ######################################################################



##### BEGIN UPDATER FUNCTIONS #####################################################################

## manual_update(.csv, .csv) -> None ; generates a .csv
## Compares two CSVs, the first containing the existing hiscores and the second the update requests
## Gets a hashtable containing hiscores from the first .csv updated per the second .csv
## Calls writecsv to write the hashtable to updated-db.csv
def manual_update(db_existing, db_updates):
  set_memberlist()
  updated = merge_csv_update(db_old_filename, update_filename)
  update_out = 'updated-db.csv'
  writecsv(updated, update_out)
  try:  diff(db_old_filename, update_out)
  except IndexError:  pass


## auto_update() -> None
def auto_update():
  print '#'*100
  wget_gdocs()
  print '\nUpdating TFS Hiscores {time}\n'.format(time=runtime)
  manual_update(db_old_filename, update_filename)
  print ''
  archive()

####### END UPDATER FUNCTIONS #####################################################################



##### BEGIN FILE I/O FUNCTIONS ####################################################################

## writecsv(dict, .csv) -> None ; generates a .csv
## Takes a hashtable of hiscore entries and writes it to the specified out_csv
def writecsv(hashtable, out_csv):
  update_writer = csv.writer(open(out_csv,'w'), dialect = 'excel')
  
  for key in hashtable :
    ## Reverses all the filtering done in update.csv_to_dict()
    ## 1st addend contains the timestamp, the rsn, and a placeholder for the notes column
    ## 2nd addend contains all the player's stats
    
    entry = [hashtable[key][-1],rsn_lookup(key),''] + hashtable[key][:-1]
    ## Create a buffer variable containing the line to write to the .csv
    
    for i in range(len(entry)) : ## Clear all the placeholders (replace zeroe with blanks)
       if entry[i] == '0' :  entry[i] = ''

    update_writer.writerow(entry)


## archive() -> None; moves all CSV files that were grabbed and written, with the exception
##                    of updated-db.csv to archive directories in the folder
def archive():
  archive_buffer = [update_filename, db_old_filename]
  for entry in archive_buffer :
    try :
      archive_dir = re.search('\.(\w+)', entry).group(1) + '_archive'
      shutil.move(entry, archive_dir)
    except IOError as error: 'IOError: could not archive {f} (action:mv)'.format(f=error.filename)
  try :
    shutil.copy('updated-db.csv','csv_archive/updated-db_{timestamp}.csv'.format(timestamp=runtime))
  except IOError as error: 'IOError: could not archive {f} (action:cp)'.format(f=error.filename)

####### END FILE I/O FUNCTIONS ####################################################################



##### BEGIN PARSER FUNCTIONS ######################################################################

## csv_to_dict(.csv, suppress_old=bool) -> dict
## Converts the CSV to a list of lines and then to a dict that it returns
## suppress_old will force list_to_dict to suppress any entries older than last_update
def csv_to_dict(filename, suppress_old=False):
 # print 'csv_to_dict called'
 # print '    on {file} with suppressing set to {suppress}'.format(file=filename, suppress=suppress_old)
 # print '    from {caller}\n'.format(caller=inspect.stack()[1][3])

  if not re.search(r'\.csv', filename):
    print 'Error: csv_to_dict() must take a CSV file as its argument.'
    print '       Filename passed to csv_to_dict() was: ' + filename
    print '       Exiting now.'
    sys.exit(1)
  
  return list_to_dict(csv_to_list(filename), print_notes=True, suppress_old=suppress_old)


## csv_to_list(.csv) -> list
## Converts the CSV to a list of lines; chops the header line if it exists
def csv_to_list(filename):
  f = open(filename, 'rU')
  lines = f.readlines() ######################### Grab the file as a list of lines
  lines = [line for line in csv.reader(lines)] ## Convert the CSV into a 2D list
  ## Note that csv.reader() defaults to using , as the delimiter and " as the escape chars
  while [] in lines :  lines.remove([])
  if lines[0][0] == 'Timestamp' :  lines.pop(0) ## Remove the header line if it exists
  return lines


## list_to_dict(list, string) -> dict
## Takes a list of hiscore entries (each entry is a list itself) and converts it into a dict
## 
## setting print_notes to True prints out notes
## setting suppress_old_prompt to True will suppress (ignore) any hiscore entries older than last_update
## 
## Returns a hashtable generated from a .csv containing player stats
##   keys are RSNs
##   values are in the form <header>, 'timestamp'
def list_to_dict(entries, print_notes=False, suppress_old=False):
  data = {} ## Initialize a data hashtable to write lines into
  
  for entry in entries :
    ## Because this goes down a file pre-sorted by timestamp, line by line, this code will automatically
    ## set the timestamp for any RSN's update to that of the latest requested update.
    ## merge_entry_update() is used to merge requested updates

    ## This method assumes that entry is formatted as follows: 'timestamp' , 'rsn' , 'note' , <header>
    ## The value that this method writes to the hashtable is in the form: <header>, 'timestamp'
    timestamp = entry[0] ########## Grab the timestamp
    rsn = strip_format(entry[1]) ## Grab the RSN
    stats = entry[3:] ############# Grab the player's stats
    
    ## Don't read old entries when suppressing old entries
    ## suppress_old_prompt  |  is_old_entry(entry)  |  add the entry to data{}?
    ##          T           |           T           |            N
    ##          T           |           F           |            Y
    ##          F           |           T           |            Y
    ##          F           |           F           |            Y
    if suppress_old and is_old_time(timestamp) :  pass
    else :
      dataset = [ int(stat) if stat.isdigit() else 0
		  for stat in [ re.sub(r'[,.\s]', '', str(stat)) for stat in stats ] ]
      ## 
      dataset.append(timestamp) ## Create the entry to write to the hashtable    
      if rsn in data.keys() : dataset = merge_entry_update(rsn, data[rsn], dataset, verify_prompt=False)
      ## Merge multiple entries
     
      data[rsn] = dataset ## Create/update the hashtable entry
      
      if print_notes and entry[2] != '' : print 'Note from {player}: {note}'.format(player=rsn_lookup(rsn), note=re.sub('\n','',entry[2]))
      ## Print the note that was left in the update request if there is one and if the method is supposed to print it.
  return data


## merge_csv_update(.csv, .csv) -> dict
## Returns a hashtable containing hiscores from the first csv updated per the second csv
def merge_csv_update(db_existing, db_updates):
  #print 'update_dict called' #DEBUGGER
  dict_existing = csv_to_dict(db_existing)
  set_prev_update_time(dict_existing) ## This must precede dict_updates, or there will be no suppression
  dict_updates = csv_to_dict(db_updates, suppress_old=True)

  #print '\nThe following players requested hiscore updates, but could not be found in the memberlist: '
  #for rsn in failed_rsn_queries :  print '   {name}'.format(name=rsn)
  #print ''

  updated_stats = dict(dict_existing) ## Create the hashtable that will be updated
  for rsn in updated_stats.keys() : ## Remove players not in the memberlist
    if rsn not in memberlist : updated_stats.pop(rsn)

  unk_updaters = list(set(dict_updates.keys()) - set(memberlist.keys()))
  if unk_updaters != [] :
    print '\nThe following players requested hiscore updates, but could not be found in the memberlist: '
    for rsn in unk_updaters :
      print '   {name}'.format(name=capitalize(rsn))
      dict_updates.pop(rsn)
    print ''

  for rsn in dict_updates :
    #if rsn in memberlist :
      if rsn not in dict_existing :  updated_stats[rsn] = dict_updates[rsn]
      else :  updated_stats[rsn] = merge_entry_update(rsn, dict_existing[rsn], dict_updates[rsn], verify_prompt=True)
    #else :
    #	    print 'The following player requested a hiscore update, but could not be found in the memberlist: {player}'.format(player=capitalize(rsn))
    
 # for rsn in updated_stats: #DEBUGGER - go through the updated hashtable (THE WHOLE THING) and print it.
   # print rsn + ': ' + str(len(updated_stats[rsn])) #DEBUGGER
    ## If line above this one is commented out, only prints lines that will be changed
    ## else, prints all lines in updated_stats (tokenizer will see it in one or the other for loop)
  return updated_stats


## merge_entry_update(string, list, list, bool) -> list
## First string is the RSN, first list contains the existing hiscore entry for RSN, second contains the update request
## Verify is a string that if set to 'yes' will make sure all updates are possible in RS
## Returns a list containing an updated hiscore entry and timestamp for RSN
def merge_entry_update(rsn, old_stats, new_stats, verify_prompt=False):
  updated_stats = list(old_stats) ## MUST cast it because otherwise, updated_stats and old_stats will be references to the same list
  
  for i in range(len(header)) : ## For every stat (levels, xp, FoG) in the hiscore entry
    try :
      new_stat = int(new_stats[i])
    except ValueError as error :
      print 'Error: {player} tried updating {stat} to {badval}'.format(player=rsn_lookup(rsn), stat=header[i], badval=new_stat[i])
    else :
      if new_stat != 0 : ## If there is an update for that stat
        if (new_stat > int(old_stats[i])) or ((new_stats[i] != old_stats[i]) and (i == 32)) :
          ## Allow updates ONLY if a person has gained level/xp; the exception is FoG rating, which *can* go down
          updated_stats[i] = new_stats[i] ## Write the update
        else :
          updated_stats[i] = old_stats[i] ## Sort of redundant, but exists as a reminder
 
 # print 'Verifying stats for', rsn_lookup(rsn), 'now... please wait.'
  if verify_prompt : updated_stats = verify(rsn, updated_stats) ## ONLY VERIFY IF PROMPTED TO DO SO
 # print old_stats
 # print updated_stats
  
  if updated_stats[:-1] != old_stats[:-1] :  updated_stats[-1] = new_stats[-1]
  ## Update the timestamp of the hiscores entry if the stats have been updated
 # print updated_stats[-1] #DEBUGGER
  return updated_stats

####### END PARSER FUNCTIONS ######################################################################


def dict_print(hashtable):
  for key in hashtable :  print capitalize(key) + ': ' + str(hashtable[key])


## Parse the command line arguments

def main():
  if len(sys.argv) < 2 or len(sys.argv) > 6:
    print 'usage: ./update.py {--<flag>} arg1 [arg2] [arg3]'
    sys.exit(1)
  
  option = sys.argv[1]
  if len(sys.argv) > 2 :  arg1 = sys.argv[2]
  if len(sys.argv) > 3 :  arg2 = sys.argv[3] # arg2 = 4th arg
  if len(sys.argv) > 4 :  arg3 = sys.argv[4] # arg3 = 5th arg
  if len(sys.argv) > 5 :  arg4 = sys.argv[5] # arg4 = 6th arg
 
  executed_yet = True
  if len(sys.argv) == 2 :
    if option == '--auto' :  auto_update()
    elif option == '--webget' :  wget_gdocs()
    elif option == '--timeset' : set_runtime()
    else : executed_yet = False
  if len(sys.argv) == 3 :
    if option == '--process' :  csv_to_dict(arg1)
    elif option == '--check' :  check(arg1)
    elif option == '--fix' :  fix(arg1)
    elif option == '--webparse' :  html_to_csv(arg1)
    elif option == '--lastupdate' : set_prev_update_time(csv_to_dict(arg1))
    else :  executed_yet = False
  if len(sys.argv) == 4 :
    if option == '--manual_update' :  manual_update(arg1, arg2)
    elif option == '--compare' :  merge_csv_update(arg1, arg2)
    elif option == '--rmentry' :  rmentry(arg1, arg2)
    elif option  == '--diff' : diff(arg1, arg2)
    else : executed_yet = False
  if len(sys.argv) == 5 :
    if option == '--rmstat' :  rmstat(arg1, arg2, arg3)
    else : executed_yet = False
  if len(sys.argv) == 6 :
    if option == '--set' :  set(arg1, arg2, arg3, arg4)
  if not executed_yet :
    print 'command not found:',
    for arg in sys.argv[1:] :  print arg,
    sys.exit(1)

if __name__ == '__main__': main()
