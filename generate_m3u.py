#!/usr/bin/env python

config = """
# the path to run the script against if no path was specified as an argument. leave blank to always require the commandline argument.
default_path:

# this script uses a keyword like "(Disc", (from something like "(Disc 1)" in the filename, used by NO-INTRO sets), to determine if a game is multi-disc.
disc_keyword: (Disc

# whether or not to skip generating m3u's for single-disc games. can be true or false
skip_singledisc: true

# the mode to operate in. choose from:
#   samefolder: just create an m3u file for each multidisc game but leave the game files untouched
#   gamefolders: create a folder per game and move the multidisc files into them, create the m3u's inside the folders. this is used by minUI
#   subfolder: create one subfolder (such as .discs) and move all the game files into it, then create m3u's in the root folder. this is what muOS uses
mode: subfolder

# if you chose to use the subfolder mode, specify the name of that folder here
subfolder_name: .discs
"""

#############
# -----------
#############

import os
import sys
import configparser

config = f"[config]\n{config}"

confparse = configparser.ConfigParser()
confparse.read_string(config)
if 'config' not in confparse.keys():
    print("ERROR: please ensure the config section is named 'config'.")
    sys.exit(1)
CONF = confparse['config']

# the usual input checking
if CONF['default_path'] and len(sys.argv) < 2:
    target_path = CONF['default_path']
else:
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} <target folder>")
        sys.exit(0)

    target_path = sys.argv[1]

if not os.path.isdir(target_path):
    print("ERROR: invalid folder")
    sys.exit(1)

if CONF['mode'] not in ('samefolder', 'gamefolders', 'subfolder'):
    print("ERROR: incorrect mode set in config!")
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
    if os.path.isdir(filename): continue

    filename_split = filename.rsplit('.', 1)
    if len(filename_split) <= 1: continue
    filename_noext, file_ext = filename.rsplit('.', 1)

    if file_ext == 'm3u':
        continue

    if file_ext in ('chd', 'bin', 'cue', 'iso'):
        gamename_split = filename_noext.rsplit(CONF['disc_keyword'], 1)
        if len(gamename_split) <= 1:
            # skip roms that don't have multiple discs, if preferred
            if CONF['skip_singledisc'] == 'true':
                continue

            pass

        gamename = gamename_split[0].strip()

        if gamename not in mapping.keys():
            mapping[gamename] = []

        mapping[gamename].append(filename)

# then use that mapping to generate the m3u's
for gamename, files in mapping.items():
    m3u_path = gamename+'.m3u'

    match CONF['mode']:
        case "gamefolders" | "subfolder":
            match CONF['mode']:
                case "gamefolders":
                    target_folder = gamename
                    m3u_path = f"{target_folder}/{m3u_path}"
                case "subfolder":
                    target_folder = CONF['subfolder_name']

            if not os.path.isdir(target_folder):
                os.mkdir(target_folder)

            for filename in files:
                os.rename(filename, f"{target_folder}/{filename}")

    # modify the m3u so that it points to the subfolder
    if CONF['mode'] == "subfolder":
        for i in range(0, len(files)):
            files[i] = f"{target_folder}/{files[i]}"

    with open(m3u_path, 'w') as fh:
        fh.write("\n".join(files))

    print(f"generated m3u for {gamename}")

if mapping:
    print()
    print("done!")
else:
    print(f"no m3u's generated for folder {target_path}")
