TTS-Backup
==========

TTS-Backup backs up Tabletop simulator save games and mods to a Zip
file, bundling locally cached images and models within a single
archive.

This only handles saves and mods in JSON format.


Requirements
------------

A Python 3 interpreter is required. For Windows users, the
`ActivePython <http://www.activestate.com/activepython/downloads>`__
distribution is recommended.


Usage
-----

All content referenced within the mod or save must have been locally
cached from within TTS before a backup can be made. Note that when
game items are contained within bags, TTS will only locally cache the
respective assets once they are removed from the bag.

By default, TTS-Backup will assume that cached data is located in
``~/Documents/My Games/Tabletop Simulator``.

Usage flags and arguments are as follows:

::

    usage: tts-backup [-h] [--gamedata PATH] [--outname FILENAME] [--dry-run]
                      [--ignore-missing] [--comment COMMENT]
                      FILENAME

    Back-up locally cached content from a TTS .json file.

    positional arguments:
      FILENAME              The save file or mod in JSON format.

    optional arguments:
      -h, --help            show this help message and exit
      --gamedata PATH       The path to the TTS game data directory.
      --outname FILENAME, -o FILENAME
                            The name for the output archive.
      --dry-run, -n         Only print which files would be backed up.
      --ignore-missing, -i  Don’t abort the backup when files are missing.
      --comment COMMENT, -c COMMENT
                            A comment to be stored in the resulting Zip.
