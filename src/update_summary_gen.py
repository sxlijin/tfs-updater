#! /usr/bin/python

import re

f = open('update.py', 'rU')

print '#'*115
print '## '

linestr = '## {0} ({1}, {2}): {3}'
fxtype = None
startline = None
endline = None
methods = []
linenum = 0

for line in f.readlines():
  linenum += 1

  match1 = re.search('##### BEGIN (.+) FUNCTIONS #+', line)
  if match1:
    fxtype = match1.group(1)
    startline = linenum
  
  match2 = re.search('def ([a-z_]+)\(', line)
  if match2:
    methods.append(match2.group(1) + '()')
  
  match3 = re.search('####### END ', line)
  if match3:
    endline = linenum
    print linestr.format(fxtype, startline, endline, re.sub('\'', '', str(methods))[1:-1])
    (fxtype, startline, endline, methods) = (None, None, None, [])

print '## '
print '#'*115
