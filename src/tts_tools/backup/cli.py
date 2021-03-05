from tts_tools.backup import backup_json
from tts_tools.libtts import GAMEDATA_DEFAULT

import argparse


parser = argparse.ArgumentParser(
    description="Back-up locally cached content from a TTS .json file."
)

parser.add_argument(
    "infile_name",
    metavar="FILENAME",
    help="The save file or mod in JSON format.",
)

parser.add_argument(
    "--gamedata",
    dest="gamedata_dir",
    metavar="PATH",
    default=GAMEDATA_DEFAULT,
    help="The path to the TTS game data dircetory.",
)

parser.add_argument(
    "--outname",
    "-o",
    dest="outfile_name",
    metavar="FILENAME",
    default=None,
    help="The name for the output archive.",
)

parser.add_argument(
    "--dry-run",
    "-n",
    dest="dry_run",
    default=False,
    action="store_true",
    help="Only print which files would be backed up.",
)

parser.add_argument(
    "--ignore-missing",
    "-i",
    dest="ignore_missing",
    default=False,
    action="store_true",
    help="Do not abort the backup when files are missing.",
)

parser.add_argument(
    "--comment",
    "-c",
    dest="comment",
    default="",
    help="A comment to be stored in the resulting Zip.",
)


def console_entry():

    args = parser.parse_args()
    backup_json(args)
