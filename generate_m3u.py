#!/usr/bin/env python

# this script uses a keyword like "(Disc", (from something like "(Disc 1)" in the filename), to determine if a game is multi-disc.
DISC_KEYWORD = "(Disc"

# whether or not to skip generating m3u's for single-disc games
SKIP_SINGLEDISC = True

# for minUI users, this'll create a folder per multi-disc game and put all the game files into it
CREATE_FOLDERS = False

#############
# -----------
#############

import os
import sys

# the usual input checking
if len(sys.argv) < 2:
    print("usage: {cmd} <target folder>".format(cmd=sys.argv[0]))
    sys.exit(0)

target_path = sys.argv[1]

if not os.path.isdir(target_path):
    print("invalid folder")
    sys.exit(1)

# get a list of all the files in the specified folder
os.chdir(target_path)
dirlist = os.listdir('.')
dirlist.sort() # make sure it's all in the right order

# create a mapping of all the files, laid out as a dictionary like this:
# {
#   "Game Name (USA)": [
#       "Game Name [USA] (Disc 1).chd"
#       "Game Name [USA] (Disc 2).chd"
#       "Game Name [USA] (Disc 3).chd"
#       "Game Name [USA] (Disc 4).chd"
#   ]
# }
mapping = {}
for filename in dirlist:
    filename_split = filename.split('.')

    if len(filename_split) == 1: continue
    if os.path.isdir(filename): continue

    filename_noext, file_ext = filename.split('.')[0], filename.split('.')[1]

    if file_ext == 'm3u':
        continue

    if file_ext in ['chd', 'bin', 'cue', 'iso']:
        gamename_split = filename_noext.split(DISC_KEYWORD)
        if len(gamename_split) == 1:
            # skip roms that don't have multiple discs, if preferred
            if SKIP_SINGLEDISC:
                continue

            pass

        gamename = gamename_split[0].strip()

        if gamename not in mapping.keys():
            mapping[gamename] = []

        mapping[gamename].append(filename)

# then use that mapping to generate the m3u's
for gamename, files in mapping.items():
    m3u_path = gamename+'.m3u'

    if CREATE_FOLDERS:
        if not os.path.isdir(gamename):
            os.mkdir(gamename)

        for filename in files:
            os.rename(filename, gamename+'/'+filename)

        m3u_path = gamename+'/'+m3u_path

    with open(m3u_path, 'w') as fh:
        fh.write("\n".join(files))

    print("generated m3u for " + gamename)

if mapping:
    print()
    print("done!")
else:
    print("no m3u's generated for folder " + target_path)
