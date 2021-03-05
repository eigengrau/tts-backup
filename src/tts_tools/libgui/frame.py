import sys
from tkinter import *

from tts_tools import util


class EntryFrame(LabelFrame):
    def __init__(self, master, *args, **kwargs):

        super().__init__(master, **kwargs)

        self.entries = []
        for (key, entry_class, entry_kwargs) in args:

            entry = entry_class(self, **entry_kwargs)
            entry.pack(fill=X)
            self.__dict__[key] = entry.var
            self.entries.append(entry)


class ButtonFrame(Frame):
    def __init__(self, master, *args):

        super().__init__(master)

        self.buttons = {}
        for label in args:

            button = Button(self, text=label)
            button.pack(side=LEFT)
            self.buttons[label] = button

    def on(self, label, command):

        self.buttons[label].config(command=command)


class OutputFrame(LabelFrame):
    def __init__(self, master, *args, **kwargs):

        super().__init__(master, *args, **kwargs)
        self.output = StreamOutput(self)
        self.output.pack(expand=True, fill=BOTH, side=LEFT)

        self.scrollbar = Scrollbar(self, command=self.output.yview)
        self.scrollbar.pack(fill=Y, side=RIGHT)
        self.output.config(yscrollcommand=self.scrollbar.set)

    def __enter__(self):

        return self.output.__enter__()

    def __exit__(self, *args):

        return self.output.__exit__(*args)

    def clear(self):

        return self.output.clear()

    def install(self):

        return self.output.install()

    def uninstall(self):

        return self.output.uninstall()


class StreamOutput(Text):
    def __init__(self, master):

        super().__init__(master)

        self.buffer = []

        self.tag_configure("err", foreground="red")

    def install(self):

        self.__enter__()
        return

    def unistall(self):

        self.__exit__()
        return

    def __enter__(self):

        # Make a proxy which replaces self.write with self.write.err,
        # so we can colorize both streams differently.
        stderr_proxy = util.ShadowProxy(proxy_for=self)
        stderr_proxy.divert_access("write", "write_err")

        self.stdout, sys.stdout = sys.stdout, self
        self.stderr, sys.stderr = sys.stderr, stderr_proxy
        return self

    def __exit__(self, *args):

        self.flush()
        sys.stdout = self.stdout
        sys.stderr = self.stderr

    def clear(self):

        self.delete(1.0, END)

    def write(self, s):

        self.buffer.append(s)
        if s.endswith("\n"):
            self.flush()

    def write_err(self, s):

        self.insert("end", s, "err")
        self.see("end")

    def flush(self):

        for elem in self.buffer:
            self.insert("end", elem)
        self.buffer = []

        self.see("end")

        return
