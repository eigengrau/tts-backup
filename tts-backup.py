#!/usr/bin/python3

import argparse
import json
import re
import os
import sys
import time
import zipfile

from libtts import (urls_from_save,
                    get_fs_path,
                    GAMEDATA_DEFAULT)


REVISION = 25


def put_metadata(zipfile, comment=None):
    """Create a MANIFEST file and store it within the archive."""

    manifest = {
        "script_revision": REVISION,
        "export_date":  round(time.time())
    }

    if comment:
        manifest['comment'] = comment

    manifest = json.dumps(manifest)
    zipfile.comment = manifest.encode("utf-8")


def parse_args():

    parser = argparse.ArgumentParser(
        description='Back-up locally cached content from a TTS .json file.'
    )

    parser.add_argument(
        'infile_name',
        metavar="FILENAME",
        help='The save file or mod in JSON format.'
    )

    parser.add_argument(
        '--gamedata',
        dest="gamedata_dir",
        metavar="PATH",
        default=GAMEDATA_DEFAULT,
        help='The path to the TTS game data directory.'
    )

    parser.add_argument(
        '--outname', '-o',
        dest="outfile_name",
        metavar="FILENAME",
        default=None,
        help='The name for the output archive.'
    )

    parser.add_argument(
        '--dry-run', '-n',
        dest="dry_run",
        default=False,
        action='store_true',
        help='Only print which files would be backed up.'
    )

    parser.add_argument(
        '--ignore-missing', '-i',
        dest="ignore_missing",
        default=False,
        action='store_true',
        help='Don’t abort the backup when files are missing.'
    )

    parser.add_argument(
        '--comment', '-c',
        dest="comment",
        default="",
        help='A comment to be stored in the resulting Zip.'
    )

    return parser.parse_args()


class ZipFile (zipfile.ZipFile):
    """A ZipFile that supports dry-runs.

    It also keeps track of files already written, and only writes them
    once. ZipFile.filelist would have been useful for this, but on
    Windows, this doesn’t seem to reflect writes before syncing the
    file to disk.
    """

    def __init__(self, *args, dry_run=False, ignore_missing=False, **kwargs):

        self.dry_run = dry_run
        self.stored_files = set()
        self.ignore_missing = ignore_missing

        if not self.dry_run:
            super(ZipFile, self).__init__(*args, **kwargs)

    def __exit__(self, *args, **kwargs):

        if not self.dry_run:
            super(ZipFile, self).__exit__(*args, **kwargs)

    def write(self, filename, *args, **kwargs):

        if filename in self.stored_files:
            return

        # Logging.
        curdir = os.getcwd()
        absname = os.path.join(curdir, filename)
        print(absname)

        if not self.dry_run:
            super(ZipFile, self).write(filename, *args, **kwargs)
        elif not (os.path.isfile(filename) or self.ignore_missing):
            raise FileNotFoundError

        self.stored_files.add(filename)


if __name__ == "__main__":

    args = parse_args()

    try:
        urls = urls_from_save(args.infile_name)
    except FileNotFoundError:
        print("File not found: %s" % args.infile_name)
        sys.exit(1)

    # Change working dir, since get_fs_path gives us a relative path.
    try:
        orig_path = os.getcwd()
        data_path = args.gamedata_dir
        os.chdir(data_path)
    except FileNotFoundError:
        print("Gamedata directory not found: %s" % args.gamedata_dir)
        sys.exit(1)

    # We also need to correct the the destination path now.
    if args.outfile_name:
        args.outfile_name = os.path.join(orig_path, args.outfile_name)
    else:
        outfile_basename = re.sub(
            r"\.json$", "",
            os.path.basename(args.infile_name)
        )
        args.outfile_name = os.path.join(orig_path, outfile_basename) + ".zip"

    # Do the job.
    with ZipFile(args.outfile_name, 'w',
                 dry_run=args.dry_run,
                 ignore_missing=args.ignore_missing) as outfile:

        for path, url in urls:

            filename = get_fs_path(path, url)
            try:
                outfile.write(filename)

            except FileNotFoundError:
                print("File not found:", filename)
                print("Aborting. Zip file is incomplete.")
                sys.exit(1)

        # Finally, include the save file itself.
        orig_json = os.path.join(orig_path, args.infile_name)
        outfile.write(orig_json, os.path.basename(args.infile_name))

        # Store some metadata.
        put_metadata(outfile, comment=args.comment)

    if not args.dry_run:
        print("All done. Backed-up contents found in", args.outfile_name)
