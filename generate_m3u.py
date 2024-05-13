#!/usr/bin/env python

import os
import sys

if len(sys.argv) < 2:
    print("usage: {cmd} <target folder>".format(cmd=sys.argv[0]))
    sys.exit(0)

target_path = sys.argv[1]

if not os.path.isdir(target_path):
    print("invalid folder")
    sys.exit(1)

os.chdir(target_path)
dirlist = os.listdir('.')
dirlist.sort()

mapping = {}
for filename in dirlist:
    filename_noext, file_ext = filename.split('.')[0], filename.split('.')[1]

    if file_ext == 'm3u':
        continue

    if file_ext in ['chd', 'iso']:
        gamename = filename_noext.split('(Disc')[0]

        if gamename not in mapping.keys():
            mapping[gamename] = []

        mapping[gamename].append(filename)

for gamename in mapping:
    with open(gamename + '.m3u', 'w') as fh:
        fh.write("\n".join(mapping[gamename]))

    print("generated m3u for " + gamename)

print()
print("done!")
