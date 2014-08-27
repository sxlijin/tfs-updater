TFS HISCORES UPDATER : Python v2.7.3

This is a command line utility that allows you to automatically update TFS hiscores.
You must have Python v2.* to run this file; Python v3.* will not work. It is recommended
that you use Python 2.7.3 when running this script.

Please note that if the format of the worksheets containing the raw data is ever 
changed, this script will have to be changed to accommodate those changes.

########################################################################################

To update the hiscores:
    Run update-hiscores.py (can be done by double-clicking it)
      Note that in Windows, it will be listed as a Python file named update-hiscores
    In Google Docs, open the db-main worksheet in TFS Hiscores
      File > Import > Choose file: updated-db.csv & Import action: Replace current sheet

Please note that the updater script will NOT update hiscores for anyone who is not listed
  in db-memberlist. This means that every  time someone joins TFS, someone must take it
  upon themselves to add that person to the memberlist.

To remove players from the hiscores, simply remove them from db-memberlist before
  running the script. 

########################################################################################

To remove players from the hiscores

If update-hiscores.py does not work for you:
    If you are on either Unix or Mac, try running chmod u+x bin/update.py
    If you are on an alternative OS, run bin/update.py (your working dir must be bin/..)

This script retrieves the CSVs published by GDocs from the TFS Hiscores, parsing them and
writing the data to a hashtable, generates a new CSV containing the updated hiscores, and
archives the retrieved hiscores.

##### The following directions explain the command line usage of this script.
##### It is recommended that you have some basic experience with CLIs to use it this way.
##### Keep in mind that to run a script in Command Prompt, you can do 'script.ext', as
##### opposed to Terminal, which requires you to run './script.ext'

##### If you have experience with Python, you can use the dir() and help() functions
##### on this script as opposed to using this README.

To run this script:
    me@hal9000:~/updater$ ./bin/update.py --<switch> [arg1] [arg2] [arg3] [arg4]
    Alternatively, you can run
      me@hal9000:~/updater$ cp bin/update.py .
    and use ./update.py instead of ./bin/update.py for all custom commands

To remove someone from the hiscores:
    me@hal9000:~/updater$ ./bin/update.py --rmentry <rsn> <db-file>
    e.g. $ update.py --rmentry 'Aging Miser' db-file.csv
         generates a new hiscores file named rmentry-out.csv where Aging Miser has been removed

To clear a selected stat of someone in the hiscores:
    me@hal9000:~/updater$ ./bin/update.py --rmstat <stat> <rsn> <db-file>
      e.g. $ update.py --rmstat 'FoG Rating' 'Aging Miser' db-file.csv
      generates a new hiscores file named setstat-out.csv where Aging Miser's FoG rating has been reset.
      Note: resetting a level sets it to 0.
            resetting experience temporarily sets it to 0; the next update will set it to the minimum
              amount of xp needed for the stated level.

To change a selected stat of someone in the hiscores:
    me@hal9000:~/updater$ ./bin/update.py --setstat <stat> <value> <rsn> <db-file>
      e.g. $ update.py --rmstat 'FoG Rating' 9000 'Aging Miser' db-file.csv
      generates a new hiscores file named setstat-out.csv where Aging Miser's FoG rating has been set to 9000.

To manually change a selected stat of someone in the hiscores:
    me@hal9000:~/updater$ ./bin/update.py --setstat <value> <stat> <rsn> <db-file>
      e.g. $ update.py --setstat 52 'Ranged level' 'Aging Miser' db-file.csv
      generates a new hiscores file named setstat-out.csv where Aging Miser's Ranged level is 52.

To check whether there are potentially conflicting entries within a hiscores file:
    me@hal9000:~/updater$ ./bin/update.py --check <db-file>
      This will return names that could be typos of one another.
      e.g. : Potential conflict between the following: Icy 001 Icy001

To show the differences between an old version of the hiscores and a new version:
    me@hal9000:~/updater$ ./bin/update.py --diff <old-file> <new-file>
      This will print out what the changes between old-file and new-file were.

To fix a hiscores file (if there is bad data - this is *not* a very smart utility):
    me@hal9000:~/updater$ ./bin/update.py --fix <db-file>
      This generates a new hiscores file named fix-out.csv.

##### Update log
2012-06-20 Wrote first version based on downloaded CSVs
2012-07-05 Built in webget(); introduced automatic download and update generation features
           via brute-force HTML parsing of published HTML
2012-07-15 Modifed download procedure to download the published CSV; removed HTML parser
           Introduced suppression of update requests older than the latest update in db-main
2012-08-03 Introduced the 'db-memberlist' worksheet to only allow updates for people in the memberlist
           New memberlist allows implementation of custom rsn capitalization
           Improved printing functionality
           Modified autoupdate scripts to append instead of overwrite update_log.txt
