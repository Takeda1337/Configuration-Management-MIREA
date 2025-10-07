import os
import tkinter
from tkinter import *
from tkinter import scrolledtext


class Shell:
    def __init__(self, root, vfsname="VFS"):
        self.root = root
        self.root.title(vfsname)

        self.text_area = scrolledtext.ScrolledText(root, wrap=tkinter.WORD, height=15, width=50, bg="black", fg="white")
        self.text_area.pack(fill=tkinter.BOTH, expand=True)
        self.text_area.insert(tkinter.END, "Введите команду, или же выйдите с помощью команды exit\n")
        self.text_area.insert(tkinter.END, "$ ")
        self.text_area.bind("<Return>", self.on_enter)

    def get_current_command(self):
        lastline = self.text_area.get("end-2l linestart", "end-1c")
        if "$" in lastline:
            return lastline.split("$", 1)[1]
        return lastline

    def on_enter(self, event):
        cmdline = self.get_current_command().strip()
        self.execute_command(cmdline)
        return "break"

    def execute_command(self, command_line):
        command_line = os.path.expandvars(command_line)
        parts = command_line.split()
        cmd = parts[0] if parts else ""
        args = parts[1:]

        if cmd == "exit":
            self.root.quit()
        if cmd == "exit":
            self.root.quit()
        elif cmd == "cd":
            self.text_area.insert(tkinter.END, f"\nНовая директория: {args}")
        elif cmd == "ls":
           self.text_area.insert(tkinter.END, f"\nПросмотр директории: {args}")
        elif cmd == "":
            self.text_area.insert(tkinter.END, "")
        else:
            self.text_area.insert(tkinter.END, f"\nОшибка: неизвестная команда '{cmd}'")

        self.text_area.insert(tkinter.END, "\n$ ")
        self.text_area.see(tkinter.END)


root = tkinter.Tk()
app = Shell(root)
root.mainloop()

