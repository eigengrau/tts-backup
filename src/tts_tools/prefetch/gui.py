from contextlib import ExitStack
from contextlib import suppress
from tkinter import BOTH
from tkinter import Frame
from tkinter import Label
from tkinter import LabelFrame
from tkinter import LEFT
from tkinter import N
from tkinter import Tk
from tkinter import X
from tkinter.font import Font
from tts_tools import libtts
from tts_tools.libgui.entry import DirEntry
from tts_tools.libgui.entry import FileEntry
from tts_tools.libgui.entry import TextEntry
from tts_tools.libgui.entry import ToggleEntry
from tts_tools.libgui.frame import ButtonFrame
from tts_tools.libgui.frame import EntryFrame
from tts_tools.libgui.frame import OutputFrame
from tts_tools.prefetch import cli
from tts_tools.prefetch import prefetch_files

import argparse
import os
import os.path
import threading


class GUI(Frame):

    argparser = argparse.ArgumentParser(
        description="Back-up locally cached content " "from a TTS .json file."
    )

    argparser.add_argument(
        "infile",
        metavar="FILENAME",
        default="",
        nargs="?",
        help="The save file or mod in JSON format.",
    )

    def __init__(self, master):

        super().__init__(master)

        self.running = None
        self.semaphore = None

        self.args = self.argparser.parse_args()

        self.make_widgets()

    def quit(self):

        if self.running and self.running.is_alive():
            self.stop()
            self.after(300, self.quit)
        else:
            super().quit()

    def make_widgets(self):

        self.label = Label(
            self, text="TTS-Prefetch", font=Font(size=14, weight="bold")
        )
        self.label.pack()

        leftpane = Frame(self)
        leftpane.configure(bg="black")

        homedir = os.path.expanduser("~")
        self.settings = EntryFrame(
            leftpane,
            (
                "infile",
                FileEntry,
                dict(
                    label="Input file",
                    initialdir=libtts.GAMEDATA_DEFAULT,
                    filetypes=[("JSON-file", "*.json")],
                    action="open",
                    default=self.args.infile,
                ),
            ),
            (
                "gamedata",
                DirEntry,
                dict(
                    label="Gamedata path",
                    default=libtts.GAMEDATA_DEFAULT,
                    initialdir=homedir,
                    mustexist=True,
                ),
            ),
            ("dry_run", ToggleEntry, dict(label="Dry run")),
            ("refetch", ToggleEntry, dict(label="Refetch")),
            ("relax", ToggleEntry, dict(label="Relax")),
            ("user_agent", TextEntry, dict(label="User-agent")),
            text="Settings",
            width=60,
        )
        self.settings.pack(fill=X)

        control = LabelFrame(leftpane, text="Control")
        self.buttons = ButtonFrame(control, "Run", "Stop", "Quit")
        self.buttons.pack()
        self.buttons.on("Run", self.run)
        self.buttons.on("Stop", self.stop)
        self.buttons.on("Quit", self.quit)
        control.pack(fill=X)

        leftpane.pack(side=LEFT, anchor=N)

        self.output = OutputFrame(self, text="Output")
        self.output.pack(expand=True, fill=BOTH)

    def run(self):

        if self.running and self.running.is_alive():
            return

        args = self.parse_args()
        if not args:
            return

        self.output.clear()

        self.semaphore = threading.Semaphore(0)

        def callback():

            with ExitStack() as stack:
                stack.enter_context(self.output)
                stack.enter_context(suppress(SystemExit))
                prefetch_files(args, self.semaphore)

        thread = threading.Thread(target=callback)
        thread.start()
        self.running = thread

    def stop(self):
        def callback():

            if self.running and self.running.is_alive():
                self.semaphore.release()
                self.running.join()

        thread = threading.Thread(target=callback)
        thread.start()

    def parse_args(self):

        commands = []

        infile = self.settings.infile.get()
        if infile:
            commands.append(infile)
        else:
            return

        gamedata = self.settings.gamedata.get()
        if gamedata:
            commands.extend(["--gamedata", gamedata])

        if self.settings.dry_run.get():
            commands.append("--dry-run")

        if self.settings.relax.get():
            commands.append("--relax")

        if self.settings.refetch.get():
            commands.append("--refetch")

        user_agent = self.settings.user_agent.get()
        if user_agent:
            commands.extend(["--user-agent", user_agent])

        return cli.parser.parse_args(args=commands)


def gui_entry():

    root = Tk()
    gui = GUI(root)
    gui.pack(fill=BOTH, expand=True)
    root.mainloop()
