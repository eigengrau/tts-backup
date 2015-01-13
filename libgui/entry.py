from tkinter import *
from tkinter import filedialog


class TextEntry (Frame):

    def __init__(self, master, *args, label, default="", **kwargs):

        super().__init__(master, *args, **kwargs)

        _, self.row = master.grid_size()

        label = label + ":"
        self.label = Label(self, text=label)
        self.label.pack(anchor=W)

        self.var = StringVar()
        self.var.set(default)
        self.entry = Entry(self, textvariable=self.var)
        self.entry.pack(side=LEFT, fill=X)


class ToggleEntry (Frame):

    def __init__(self, master, *args, label, **kwargs):

        super().__init__(master, *args, **kwargs)

        _, self.row = master.grid_size()

        self.var = BooleanVar()
        self.checkbutton = Checkbutton(self, variable=self.var)
        self.checkbutton.pack(side=LEFT)

        self.label = Label(self, text=label)
        self.label.pack(anchor=W)
        self.label.bind("<Button-1>", self.toggle)

    def toggle(self, *args):

        oldval = self.var.get()
        self.var.set(not oldval)


class FSEntry (TextEntry):

    def __init__(self, *args, initialdir=None, mustexist=False, **kwargs):

        super().__init__(*args, **kwargs)

        self.button = Button(self,
                             text="...",
                             command=self.ask,
                             font=font.Font(size=6))
        self.button.pack(side=RIGHT)

        self.initialdir = initialdir
        self.mustexist = mustexist

    def ask(self):

        raise NotImplementedError


class FileEntry (FSEntry):

    def __init__(self,
                 *args,
                 filetypes=[],
                 defaultextension="",
                 action,
                 **kwargs):

        super().__init__(*args, **kwargs)
        self.defaultextension = defaultextension
        self.filetypes = filetypes

        if action == "save":
            self.ask_func = filedialog.asksaveasfilename
        elif action == "open":
            self.ask_func = filedialog.askopenfilename
        else:
            raise TypeError("Unknown action type: %s" % action)

    def ask(self):

        filename = self.ask_func(initialdir=self.initialdir,
                                 filetypes=self.filetypes,
                                 defaultextension=self.defaultextension)
        self.var.set(filename)


class DirEntry (FSEntry):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    def ask(self):

        dirname = filedialog.askdirectory(initialdir=self.initialdir,
                                          mustexist=self.mustexist)
        self.var.set(dirname)
