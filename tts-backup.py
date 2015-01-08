#!/usr/bin/python3

import argparse
import json
import re
import os
import sys
import time

from zipfile import ZipFile


REVISION = 17

IMGPATH = os.path.join("Mods", "Images")
OBJPATH = os.path.join("Mods", "Models")

GAMEDATA_DEFAULT = os.path.expanduser(
    "~/Documents/My Games/Tabletop Simulator"
)


def seekURL(dic, trail=[]):
    """Recursively search through the save game structure and return URLs
    and the paths to them.

    """

    for k, v in dic.items():

        newtrail = trail + [k]

        if isinstance(v, dict):
            yield from seekURL(v, newtrail)

        elif isinstance(v, list):
            for elem in v:
                if not isinstance(elem, dict):
                    continue
                yield from seekURL(elem, newtrail)

        elif k.endswith("URL"):
            # Some URL keys may be left empty.
            if not v:
                continue

            # Deck art URLs can contain metadata in curly braces
            # (yikes).
            v = re.sub(r"{.*}", "", v)

            yield (newtrail, v)


# We need checks for whether a URL points to a mesh or an image, so we
# can do the right thing for each.

def is_obj(path, url):
    # TODO: None of my mods have NormalURL set (normal maps?). I’m
    # assuming these are image files.
    obj_keys = ("MeshURL", "ColliderURL")
    return path[-1] in obj_keys


def is_image(path, url):
    # This assumes that we only have mesh and image URLs.
    return not is_obj(path, url)


def recodeURL(url):
    """Recode the given URL in the way TTS does, which yields the
    file-system path to the cached file."""

    return re.sub(r"[\W_]", "", url)


def get_fs_path(path, url):
    """Return a file-system path to the object in the cache."""

    recoded_name = recodeURL(url)

    if is_obj(path, url):
        filename = recoded_name + ".obj"
        return os.path.join(OBJPATH, filename)

    elif is_image(path, url):
        # Evenn PNGs are stored with .jpg suffix by TTS.
        filename = recoded_name + ".jpg"
        return os.path.join(IMGPATH, filename)

    else:
        raise ValueError("Don’t know how to generate path for URL %s at %s." %
                         (url, path))


def put_metadata(zipfile):
    """Create a MANIFEST file and store it within the archive."""

    manifest = {
        "script_revision": REVISION,
        "export_date":  round(time.time())
    }

    manifest = json.dumps(manifest)
    zipfile.comment = manifest.encode("utf-8")


def urls_from_save(filename):

    infile = open(args.infile_name, "r")
    save = json.load(infile)
    return seekURL(save)


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

    return parser.parse_args()


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
    with ZipFile(args.outfile_name, 'w') as outfile:

        for path, url in urls:

            filename = get_fs_path(path, url)

            if not os.path.isfile(filename):
                print("File not found:", filename)
                print("Aborting. Zip file is incomplete.")
                sys.exit(1)

            # Some files might be referred to multiple times in the save
            # game. Only store them once.
            if filename not in outfile.namelist():
                print(filename)
                outfile.write(filename)

        print()

        # Finally, include the save file itself.
        orig_json = os.path.join(orig_path, args.infile_name)
        outfile.write(orig_json, os.path.basename(args.infile_name))

        # Store some metadata.
        put_metadata(outfile)

    print("All done. Backed-up contents found in", args.outfile_name)
