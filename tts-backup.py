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


REVISION = 28


parser = argparse.ArgumentParser(
    description="Back-up locally cached content from a TTS .json file."
)

parser.add_argument(
    'infile_name',
    metavar='FILENAME',
    help="The save file or mod in JSON format."
)

parser.add_argument(
    "--gamedata",
    dest='gamedata_dir',
    metavar='PATH',
    default=GAMEDATA_DEFAULT,
    help="The path to the TTS game data directory."
)

parser.add_argument(
    "--outname", '-o',
    dest='outfile_name',
    metavar='FILENAME',
    default=None,
    help="The name for the output archive."
)

parser.add_argument(
    "--dry-run", "-n",
    dest='dry_run',
    default=False,
    action='store_true',
    help="Only print which files would be backed up."
)

parser.add_argument(
    "--ignore-missing", "-i",
    dest='ignore_missing',
    default=False,
    action='store_true',
    help="Do not abort the backup when files are missing."
)

parser.add_argument(
    "--comment", "-c",
    dest="comment",
    default="",
    help="A comment to be stored in the resulting Zip."
)


class ZipFile (zipfile.ZipFile):
    """A ZipFile that supports dry-runs.

    It also keeps track of files already written, and only writes them
    once. ZipFile.filelist would have been useful for this, but on
    Windows, this doesn’t seem to reflect writes before syncing the
    file to disk.
    """

    def __init__(self, *args,
                 dry_run=False,
                 ignore_missing=False,
                 **kwargs):

        self.dry_run = dry_run
        self.stored_files = set()
        self.ignore_missing = ignore_missing

        if not self.dry_run:
            super().__init__(*args, **kwargs)

    def __exit__(self, *args, **kwargs):

        if not self.dry_run:
            super().__exit__(*args, **kwargs)

    def write(self, filename, *args, **kwargs):

        if filename in self.stored_files:
            return

        # Logging.
        curdir = os.getcwd()
        absname = os.path.join(curdir, filename)
        log_skipped = lambda: print("%s (not found)" % absname)
        log_written = lambda: print(absname)

        if not (os.path.isfile(filename) or self.ignore_missing):
            raise FileNotFoundError("No such file: {}".format(filename))

        if self.dry_run and os.path.isfile(filename):
            log_written()

        elif self.dry_run:
            log_skipped()

        else:
            try:
                super().write(filename, *args, **kwargs)
                log_written()
            except FileNotFoundError:
                assert self.ignore_missing
                log_skipped()

        self.stored_files.add(filename)

    def put_metadata(self, comment=None):
        """Create a MANIFEST file and store it within the archive."""

        manifest = {
            "script_revision": REVISION,
            "export_date":  round(time.time())
        }

        if comment:
            manifest['comment'] = comment

        manifest = json.dumps(manifest)
        self.comment = manifest.encode('utf-8')


def main(args):

    try:
        urls = urls_from_save(args.infile_name)
    except FileNotFoundError as error:
        errmsg = "Could not read URLs from '{file}': {error}".format(
            file=args.infile_name,
            error=error.strerror
        )
        print(errmsg, file=sys.stderr)
        sys.exit(1)

    # Change working dir, since get_fs_path gives us a relative path.
    try:
        orig_path = os.getcwd()
        data_path = args.gamedata_dir
        os.chdir(data_path)
    except FileNotFoundError as error:
        errmsg = "Could not open gamedata directory '{dir}': {error}".format(
            dir=args.gamedata_dir,
            error=error.strerror
        )
        print(errmsg, file=sys.stderr)
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

            except FileNotFoundError as error:
                errmsg = "Could not write {filename} to Zip ({error}).".format(
                    filename=filename,
                    error=error.strerror
                )
                print(errmsg, "Aborting.", sep='\n', file=sys.stderr)
                if not args.dry_run:
                    print("Zip file is incomplete.", file=sys.stderr)
                sys.exit(1)

        # Finally, include the save file itself.
        orig_json = os.path.join(orig_path, args.infile_name)
        outfile.write(orig_json, os.path.basename(args.infile_name))

        # Store some metadata.
        outfile.put_metadata(comment=args.comment)

    if args.dry_run:
        print("Dry run for %s completed." % args.infile_name)
    else:
        print("Backed-up contents for %s found in %s." %
              (args.infile_name, args.outfile_name))


if __name__ == '__main__':

    args = parser.parse_args()
    main(args)
