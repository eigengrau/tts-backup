import json
import zipfile
import os
import time
import pkg_resources


REVISION = pkg_resources.require("tts-backup")[0].version


class ShadowProxy:
    """Proxy objects for arbitrary objects, with the ability to divert
    attribute access from one attribute to another.

    """

    def __init__(self, proxy_for):
        self.__target = proxy_for
        self.__diverted = {}

    def divert_access(self, source, target):
        self.__diverted[source] = target

    def __getattr__(self, name):
        if name in self.__diverted:
            name = self.__diverted[name]
        return getattr(self.__target, name)


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
        log_skipped = lambda: print("{} (not found)".format(absname))
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
            except FileNotFoundError:
                assert self.ignore_missing
                log_skipped()
            else:
                log_written()

        self.stored_files.add(filename)

    def put_metadata(self, comment=None):
        """Create a MANIFEST file and store it within the archive."""

        manifest = dict(script_revision=REVISION,
                        export_date=round(time.time()))

        if comment:
            manifest['comment'] = comment

        manifest = json.dumps(manifest)
        self.comment = manifest.encode('utf-8')


def print_err(*args, **kwargs):
    # stderr could be reset at run-time, so we need to import it when
    # the function runs, not when this module is imported.
    from sys import stderr
    if 'file' in kwargs:
        del kwargs['file']
    print(*args, file=stderr, **kwargs)
