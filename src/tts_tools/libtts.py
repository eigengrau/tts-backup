import json
import re
import os
import platform

IMGPATH = os.path.join("Mods", "Images")
OBJPATH = os.path.join("Mods", "Models")
BUNDLEPATH = os.path.join("Mods", "Assetbundles")
AUDIOPATH = os.path.join("Mods", "Audio")
PDFPATH = os.path.join("Mods", "PDF")

gamedata_map = {
  'Windows': '~/Documents/My Games/Tabletop Simulator',
  'Darwin': '~/Library/Tabletop Simulator', # MacOS
  'Linux': '~/.local/share/Tabletop Simulator',
}
try:
  active_platform = platform.system()
  GAMEDATA_DEFAULT = os.path.expanduser(gamedata_map[active_platform])
except KeyError:
  GAMEDATA_DEFAULT = os.path.expanduser(gamedata_map['Windows'])


class IllegalSavegameException (ValueError):

    def __init__(self):
        super().__init__("not a Tabletop Simulator savegame")


def seekURL(dic, trail=[]):
    """Recursively search through the save game structure and return URLs
    and the paths to them.

    """

    for k, v in dic.items():

        newtrail = trail + [k]

        if k == "AudioLibrary":
            for elem in v:
                try:
                    # It appears that AudioLibrary items are mappings of form
                    # “Item1” → URL, “Item2” → audio title.
                    yield (newtrail, elem["Item1"])
                except KeyError:
                    raise NotImplementedError(
                        "AudioLibrary has unexpected structure: {}".format(v)
                    )

        elif isinstance(v, dict):
            yield from seekURL(v, newtrail)

        elif isinstance(v, list):
            for elem in v:
                if not isinstance(elem, dict):
                    continue
                yield from seekURL(elem, newtrail)

        elif k.lower().endswith("url"):
            # We don’t want tablet URLs.
            if k == "PageURL":
                continue

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
    # This assumes that we only have mesh, assetbundle, audio, PDF and image
    # URLs.
    return not (
        is_obj(path, url)
        or is_assetbundle(path, url)
        or is_audiolibrary(path, url)
        or is_pdf(path, url)
    )


def is_assetbundle(path, url):
    bundle_keys = ("AssetbundleURL", "AssetbundleSecondaryURL")
    return path[-1] in bundle_keys


def is_audiolibrary(path, url):
    audio_keys = ("CurrentAudioURL", "AudioLibrary")
    return path[-1] in audio_keys


def is_pdf(path, url):
    return path[-1] == "PDFUrl"


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

    elif is_assetbundle(path, url):
        filename = recoded_name + ".unity3d"
        return os.path.join(BUNDLEPATH, filename)

    elif is_audiolibrary(path, url):
        # Is the suffix always MP3, regardless of content?
        filename = recoded_name + ".MP3"
        return os.path.join(AUDIOPATH, filename)

    elif is_pdf(path, url):
        filename = recoded_name + ".PDF"
        return os.path.join(PDFPATH, filename)

    elif is_image(path, url):
        # TTS appears to perform some weird heuristics when determining
        # the file suffix. ._.
        if url.find(".png") > 0:
            file_suffix = ".png"
        else:
            file_suffix = ".jpg"
        filename = recoded_name + file_suffix
        return os.path.join(IMGPATH, filename)

    else:
        errstr = ("Do not know how to generate path for "
                  "URL {url} at {path}.".format(url=url, path=path))
        raise ValueError(errstr)


def urls_from_save(filename):

    with open(filename, 'r', encoding='utf-8') as infile:
        try:
            save = json.load(infile)
        except UnicodeDecodeError:
            raise IllegalSavegameException

    if not isinstance(save, dict):
        raise IllegalSavegameException

    return seekURL(save)


def get_save_name(filename):

    with open(filename, 'r', encoding='utf-8') as infile:
        save = json.load(infile)
    return save["SaveName"]
