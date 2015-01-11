TTS-Backup
==========

TTS-Backup backs up Tabletop simulator save games and mods to a Zip
file, bundling locally cached images and models within a single
archive.

This only handles saves and mods in JSON format.


Requirements & Installation
---------------------------

A Python 3 interpreter is required. For Windows users, the
`ActivePython <http://www.activestate.com/activepython/downloads>`__
distribution is recommended.

To install, simply copy all source files into a directory of your
convenience.


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


TTS-Prefetch
============

TTS-Prefetch downloads assets specified within a TTS JSON save file
and stores them within the TTS cache. This is handy if you want to
ensure that all mod assets are present, e. g., when several mods have
been updated, or when a mod uses bags, which normally require that all
pieces are unpacked manually before they are fetched and stored inside
the TTS cache.


Requirements & Installation
---------------------------

Cf. above.


Usage
-----

By default, TTS-Prefetch will assume that cached data is located in
``~/Documents/My Games/Tabletop Simulator``.

Usage flags and arguments are as follows:

::

    usage: tts-prefetch [-h] [--gamedata PATH] [--dry-run] [--refetch] [--relax]
                        FILENAME

    Download assets referenced in TTS .json files.

    positional arguments:
      FILENAME         The save file or mod in JSON format.

    optional arguments:
      -h, --help       show this help message and exit
      --gamedata PATH  The path to the TTS game data directory.
      --dry-run, -n    Only print which files would be downloaded.
      --refetch, -r    Rewrite objects that already exists in the cache.
      --relax, -x      Don’t abort when encountering an unexpected MIME type.
