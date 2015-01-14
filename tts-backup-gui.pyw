#!/usr/bin/env python
# Shared GUI functions & classes.

import os
import os.path
import threading
import argparse

from tkinter import *
from tkinter.font import Font

from libgui.entry import (
    DirEntry,
    FileEntry,
    TextEntry,
    ToggleEntry
)
from libgui.frame import (
    EntryFrame,
    ButtonFrame,
    OutputFrame
)

import libtts
tts_backup = __import__('tts-backup')


class GUI (Frame):

    argparser = argparse.ArgumentParser(
        description="Back-up locally cached content "
                    "from a TTS .json file."
    )

    argparser.add_argument('infile',
                           metavar='FILENAME',
                           default='',
                           nargs='?',
                           help="The save file or mod in JSON format.")

    def __init__(self, master):

        super().__init__(master)

        self.running = None
        self.args = self.argparser.parse_args()

        self.make_widgets()

    def make_widgets(self):

        self.label = Label(self,
                           text="TTS-Backup",
                           font=Font(size=14, weight='bold'))
        self.label.pack()

        leftpane = Frame(self)

        homedir = os.path.expanduser("~")
        self.settings = EntryFrame(
            leftpane,

            ('infile',   FileEntry, dict(label="Input file",
                                         initialdir=libtts.GAMEDATA_DEFAULT,
                                         filetypes=[("JSON-file", "*.json")],
                                         action='open')),
            ('gamedata', DirEntry,  dict(label="Gamedata path",
                                         default=libtts.GAMEDATA_DEFAULT,
                                         initialdir=homedir,
                                         mustexist=True)),
            ('outfile',  FileEntry, dict(label="Output archive",
                                         initialdir=homedir,
                                         defaultextension=".zip",
                                         action='save')),
            ('comment',  TextEntry, dict(label="Archive comment")),

            ('dry_run',        ToggleEntry, dict(label="Dry run")),
            ('ignore_missing', ToggleEntry, dict(label="Ignore missing")),

            text="Settings",
            width=60
        )
        self.settings.infile.trace('w', self.on_infile_change)
        self.settings.infile.set(self.args.infile)
        self.settings.pack(fill=X)

        control = LabelFrame(leftpane, text="Control")
        self.buttons = ButtonFrame(control, 'Run', 'Quit')
        self.buttons.pack()
        self.buttons.on('Quit', self.quit)
        self.buttons.on('Run', self.run)
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

        def callback():
            with self.output:
                try:
                    tts_backup.main(args)
                except SystemExit:
                    pass

        thread = threading.Thread(target=callback)
        thread.start()
        self.running = thread

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

        outfile = self.settings.outfile.get()
        if outfile:
            commands.extend(["--outname", outfile])

        if self.settings.dry_run.get():
            commands.append("--dry-run")

        if self.settings.ignore_missing.get():
            commands.append("--ignore-missing")

        comment = self.settings.comment.get()
        if comment:
            commands.extend(["--comment", comment])

        return tts_backup.parser.parse_args(args=commands)

    def on_infile_change(self, *args):

        filename = self.settings.infile.get()
        filename = os.path.basename(filename)
        filename = re.sub(r"\.json$", "", filename)

        if filename:
            filename += ".zip"
            filename = os.path.join(os.path.expanduser("~"), filename)
            self.settings.outfile.set(filename)


if __name__ == '__main__':

    root = Tk()
    gui = GUI(root)
    gui.pack(fill=BOTH, expand=True)
    root.mainloop()
