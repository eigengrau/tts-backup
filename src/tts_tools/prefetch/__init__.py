from contextlib import suppress
from tts_tools.libtts import GAMEDATA_DEFAULT
from tts_tools.libtts import get_fs_path
from tts_tools.libtts import get_save_name
from tts_tools.libtts import IllegalSavegameException
from tts_tools.libtts import is_assetbundle
from tts_tools.libtts import is_audiolibrary
from tts_tools.libtts import is_image
from tts_tools.libtts import is_obj
from tts_tools.libtts import is_pdf
from tts_tools.libtts import urls_from_save
from tts_tools.util import print_err

import http.client
import os
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request


def prefetch_file(
    filename,
    refetch=False,
    ignore_content_type=False,
    dry_run=False,
    gamedata_dir=GAMEDATA_DEFAULT,
    timeout=5,
    semaphore=None,
    user_agent="TTS prefetch",
):

    try:
        save_name = get_save_name(filename)
    except Exception:
        save_name = "???"

    print(
        "Prefetching assets for {file} ({save_name}).".format(
            file=filename, save_name=save_name
        )
    )

    try:
        urls = urls_from_save(filename)
    except (FileNotFoundError, IllegalSavegameException) as error:
        print_err(
            "Error retrieving URLs from {filename}: {error}".format(
                error=error, filename=filename
            )
        )
        raise

    done = set()
    for path, url in urls:

        if semaphore and semaphore.acquire(blocking=False):
            print("Aborted.")
            return

        # Some mods contain malformed URLs missing a prefix. I’m not
        # sure how TTS deals with these. Let’s assume http for now.
        if not urllib.parse.urlparse(url).scheme:
            print_err(
                "Warning: URL {url} does not specify a URL scheme. "
                "Assuming http.".format(url=url)
            )
            fetch_url = "http://" + url
        else:
            fetch_url = url

        # A mod might refer to the same URL multiple times.
        if url in done:
            continue

        # To prevent downloading unexpected content, we check the MIME
        # type in the response.
        if is_obj(path, url):

            def content_expected(mime):
                any(
                    map(
                        mime.startswith,
                        (
                            "text/plain",
                            "application/binary",
                            "application/octet-stream",
                            "application/json",
                            "application/x-tgif",
                        ),
                    )
                )

        elif is_assetbundle(path, url):

            def content_expected(mime):
                any(
                    map(
                        mime.startswith,
                        ("application/binary", "application/octet-stream"),
                    )
                )

        elif is_image(path, url):

            def content_expected(mime):
                mime in (
                    "image/jpeg",
                    "image/jpg",
                    "image/png",
                    "application/octet-stream",
                    "application/binary",
                    "video/mp4",
                )

        elif is_audiolibrary(path, url):

            def content_expected(mime):
                mime in (
                    "application/octet-stream",
                    "application/binary",
                ) or mime.startswith("audio/")

        elif is_pdf(path, url):

            def content_expected(mime):
                mime in (
                    "application/pdf",
                    "application/binary",
                    "application/octet-stream",
                )

        else:
            errstr = "Do not know how to retrieve URL {url} at {path}.".format(
                url=url, path=path
            )
            raise ValueError(errstr)

        outfile_name = os.path.join(gamedata_dir, get_fs_path(path, url))

        # Check if the object is already cached.
        if os.path.isfile(outfile_name) and not refetch:
            done.add(url)
            continue

        print("{} ".format(url), end="", flush=True)

        if dry_run:
            print("dry run")
            done.add(url)
            continue

        headers = {"User-Agent": user_agent}
        request = urllib.request.Request(url=fetch_url, headers=headers)

        try:
            response = urllib.request.urlopen(request, timeout=timeout)

        except urllib.error.HTTPError as error:
            print_err(
                "Error {code} ({reason})".format(
                    code=error.code, reason=error.reason
                )
            )
            continue

        except urllib.error.URLError as error:
            print_err("Error ({reason})".format(reason=error.reason))
            continue

        except socket.timeout as error:
            print_err("Error ({reason})".format(reason=error))
            continue

        except http.client.HTTPException as error:
            print_err("HTTP error ({reason})".format(reason=error))
            continue

        # Only for informative purposes.
        length = response.getheader("Content-Length", 0)
        length_kb = "???"
        if length:
            with suppress(ValueError):
                length_kb = int(length) / 1000
        size_msg = "({length} kb): ".format(length=length_kb)
        print(size_msg, end="", flush=True)

        content_type = response.getheader("Content-Type", "").strip()
        is_expected = not content_type or content_expected(content_type)
        if not (is_expected or ignore_content_type):
            print_err(
                "Error: Content type {type} does not match expected type. "
                "Aborting. Use --relax to ignore.".format(type=content_type)
            )
            sys.exit(1)

        try:
            with open(outfile_name, "wb") as outfile:
                outfile.write(response.read())

        except FileNotFoundError as error:
            print_err("Error writing object to disk: {}".format(error))
            raise

        # Don’t leave files with partial content lying around.
        except Exception:
            with suppress(FileNotFoundError):
                os.remove(outfile_name)
            raise

        else:
            print("ok")

        if not is_expected:
            errmsg = (
                "Warning: Content type {} did not match "
                "expected type.".format(content_type)
            )
            print_err(errmsg)

        done.add(url)

    if dry_run:
        completion_msg = "Dry-run for {} completed."
    else:
        completion_msg = "Prefetching {} completed."
    print(completion_msg.format(filename))


def prefetch_files(args, semaphore=None):

    for infile_name in args.infile_names:

        try:
            prefetch_file(
                infile_name,
                dry_run=args.dry_run,
                refetch=args.refetch,
                ignore_content_type=args.ignore_content_type,
                gamedata_dir=args.gamedata_dir,
                timeout=args.timeout,
                semaphore=semaphore,
                user_agent=args.user_agent,
            )

        except (FileNotFoundError, IllegalSavegameException, SystemExit):
            print_err("Aborting.")
            sys.exit(1)
