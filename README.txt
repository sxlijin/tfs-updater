This file is part of TFS HISCORES UPDATER.

################################################################################

TFS HISCORES UPDATER : Python 2.7.*

This is a script that allows you to automatically update TFS hiscores. You 
must have Python v2.* to run this file; Python 3.* will not work. This script
was originally developed using Python 2.7.3, but any 2.7 flavor of Python
should be compatible.

Please note that if the format of the worksheets containing the raw data is ever 
changed, this script will have to be changed to accommodate those changes.

################################################################################

To update the hiscores:
    Run update-hiscores.py (can be done by double-clicking it)
      Note that in Windows, it will show up as update-hiscores.
    In Google Docs, open the db-main worksheet in TFS Hiscores
      File > Import > Choose file: updated-db.csv
	Import action: Replace current sheet

Please note that the updater script will NOT update hiscores for anyone who is 
not listed in db-memberlist. This means that every  time someone joins TFS,
someone must take it upon themselves to add that person to the memberlist.

To remove players from the hiscores, simply remove them from db-memberlist
before running the script. 

################################################################################

If update-hiscores.py does not work for you:
    If you are on either Unix or Mac, try running chmod u+x src/update.py
    If you are on an alternative OS, run src/update.py (your working dir must
      be src/..)

This script retrieves the automatically generated CSV data of a player's
hiscores, reads it all into hashtables, then generates a CSV to upload to
GDocs.

##### Update log
2016-04-05:v2.2 Refactored to include all dependencies. Should be able to run
        independently of any and all library dependencies, barring the standard
        Python 2.7.x distribution.
            Bug fixes made along the way also apparently never actually worked
        correctly. That's completely on me for not testing after commit/push. 
            Independency required some refactoring to make stuff work; what 
        happened was that by moving all dependencies in, a lot of the import
        statements in the dependencies themselves no longer worked, because
        they were attempting to do a global import, instead of a submodule
        import - which is where the dependency had been placed. The following
        sed statement was required to repair these dependencies:
            sed -i "s/^import six$/import lib.six as six/;
                    s/^from six/from lib.six/;
                    s/^import chardet$/import lib.chardet as chardet/;
                    s/^from urllib3/from lib.urllib3/
                    " lib/*/*.py
2014-09-01:v2.1 Reorganized file structure.
2014-06-05:v2.0	Completely rewrote everything following Jagex's decision to 
		return hiscores to the F2P community. New version completely 
		ditches input sanitization or timestamp cross-checking or 
		anything of the sort that v1.* dealt with. It assume Jagex's
		data is good and just runs with it, but also implements the
		requests library to deal with 301 redirects that Jagex uses.
2012-08-03:v1.3	Introduced the 'db-memberlist' worksheet to only allow updates
		for people in the memberlist; new memberlist allows 
		implementation of custom rsn capitalization; improved printing 
		functionality; modified autoupdate scripts to append instead of 
		overwrite update_log.txt
2012-07-15:v1.2	Modifed download procedure to download the published CSV;
		removed homemade HTML parser; introduced suppression of update 
		requests older than the latest update in db-main
2012-07-05:v1.1	Built in webget(); introduced automatic download and update 
		generation features via brute-force parsing of published HTML
2012-06-20:v1.0	Wrote first version based on downloaded CSVs
