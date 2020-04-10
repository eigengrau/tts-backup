import re
import os
import sys

from tts_tools.util import (
    ZipFile,
    print_err
)
from tts_tools.libtts import (
    urls_from_save,
    get_fs_path,
    IllegalSavegameException
)


def backup_json(args):

    try:
        urls = urls_from_save(args.infile_name)
    except (FileNotFoundError, IllegalSavegameException) as error:
        errmsg = "Could not read URLs from '{file}': {error}".format(
            file=args.infile_name,
            error=error
        )
        print_err(errmsg)
        sys.exit(1)

    # Change working dir, since get_fs_path gives us a relative path.
    orig_path = os.getcwd()
    try:
        os.chdir(args.gamedata_dir)
    except FileNotFoundError as error:
        errmsg = "Could not open gamedata directory '{dir}': {error}".format(
            dir=args.gamedata_dir,
            error=error
        )
        print_err(errmsg)
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

    try:
        zipfile = ZipFile(args.outfile_name, 'w',
                          dry_run=args.dry_run,
                          ignore_missing=args.ignore_missing)
    except FileNotFoundError as error:
        errmsg = "Could not write to Zip archive '{outfile}': {error}".format(
            outfile=args.outfile_name,
            error=error
        )
        print_err(errmsg)
        sys.exit(1)

    with zipfile as outfile:

        for path, url in urls:

            filename = get_fs_path(path, url)
            try:
                outfile.write(filename)

            except FileNotFoundError as error:
                errmsg = "Could not write {filename} to Zip ({error}).".format(
                    filename=filename,
                    error=error
                )
                print_err(errmsg, "Aborting.", sep="\n", end=" ")
                if not args.dry_run:
                    print_err("Zip file is incomplete.")
                else:
                    print_err()
                sys.exit(1)

        # Finally, include the save file itself.
        orig_json = os.path.join(orig_path, args.infile_name)
        outfile.write(orig_json, os.path.basename(args.infile_name))

        # Store some metadata.
        outfile.put_metadata(comment=args.comment)

    if args.dry_run:
        print("Dry run for {file} completed.".format(file=args.infile_name))
    else:
        print("Backed-up contents for {file} found in {outfile}.".format(
            file=args.infile_name,
            outfile=args.outfile_name
        ))
