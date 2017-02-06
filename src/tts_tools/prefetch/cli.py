import argparse
import sys
import signal

from tts_tools.libtts import GAMEDATA_DEFAULT
from tts_tools.prefetch import prefetch_files


parser = argparse.ArgumentParser(
    description="Download assets referenced in TTS .json files."
)

parser.add_argument(
    'infile_names',
    metavar='FILENAME',
    nargs='+',
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
    "--dry-run", "-n",
    dest='dry_run',
    default=False,
    action='store_true',
    help="Only print which files would be downloaded."
)

parser.add_argument(
    "--refetch", "-r",
    dest='refetch',
    default=False,
    action='store_true',
    help="Rewrite objects that already exist in the cache."
)

parser.add_argument(
    "--relax", "-x",
    dest='ignore_content_type',
    default=False,
    action='store_true',
    help="Do not abort when encountering an unexpected MIME type."
)

parser.add_argument(
    "--timeout", "-t",
    dest='timeout',
    default=5,
    type=int,
    help="Connection timeout in s."
)
parser.add_argument(
    "--user-agent", "-a",
    dest="user_agent",
    default="tts-backup",
    help="HTTP user-agent string."
)


def sigint_handler(signum, frame):
    sys.exit(1)


def console_entry():

    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigint_handler)
    args = parser.parse_args()
    prefetch_files(args)
