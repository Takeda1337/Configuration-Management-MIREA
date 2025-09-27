import os
import sys
import argparse
import tkinter
from tkinter import *
from tkinter import scrolledtext

class Shell:
    def __init__(self, root, vfs_root=None, startup_script=None, debug_params=None):
        self.root = root
        self.root.title("Эмулятор VFS")
        
        self.vfs_root = os.path.abspath(vfs_root) if vfs_root else os.getcwd()
        if not os.path.exists(self.vfs_root):
            os.makedirs(self.vfs_root)
        self.current_dir = self.vfs_root

        self.text_area = scrolledtext.ScrolledText(root, wrap="word", height=20, width=80,
                                                   bg="black", fg="white")
        self.text_area.pack(fill="both", expand=True)
        self.text_area.insert("end", "Введите команду, или введите команду 'exit' для выхода\n")
        self.text_area.insert("end", "Стартовые параметры:\n")
        if debug_params:
            for k, v in debug_params.items():
                self.text_area.insert("end", f"  {k}: {v}\n")
        self.text_area.insert("end", f"Путь к VFS: {self.vfs_root}\n")
        self.text_area.insert("end", f"Текущая директория: {self.current_dir}\n")
        self.text_area.insert("end", "$ ")
        self.text_area.see("end")
        self.root.update_idletasks()
        self.text_area.bind("<Return>", self.on_enter)


        if startup_script:
            self.run_startup_script(startup_script)

    def get_current_command(self):
        lastline = self.text_area.get("end-2l linestart", "end-1c")
        if "$" in lastline:
            return lastline.split("$", 1)[1]
        return lastline


    def on_enter(self, event):
        cmd = self.get_current_command().strip()
        self.execute_command(cmd)
        return "break"


    def execute_command(self, command_line, echo_input=True):
        command_line = os.path.expandvars(command_line)
        parts = command_line.split()
        cmd = parts[0] if parts else ""
        args = parts[1:]

        if cmd == "":
            self.text_area.insert("end", "\n$ ")
            self.text_area.see("end")
            self.root.update_idletasks()
            return True

        if cmd == "exit":
            self.text_area.insert("end", "\nВыход из эмулятора...\n")
            self.text_area.see("end")
            self.root.update_idletasks()
            self.root.quit()
            return True

        if cmd == "cd":
            target = args[0] if args else self.vfs_root
            new_path = os.path.abspath(os.path.join(self.current_dir, target))
            if not new_path.startswith(self.vfs_root) or not os.path.isdir(new_path):
                self.text_area.insert("end", f"\nОшибка: '{target}' не является директорией или недоступна")
                self.text_area.insert("end", "\n$ ")
                self.text_area.see("end")
                self.root.update_idletasks()
                return False
            self.current_dir = new_path
            self.text_area.insert("end", f"\nДиректория изменена на: {self.current_dir}")
            self.text_area.insert("end", "\n$ ")
            self.text_area.see("end")
            self.root.update_idletasks()
            return True

        if cmd == "ls":
            entries = os.listdir(self.current_dir)
            self.text_area.insert("end", "\n" + "\n".join(entries) if entries else "\n(пусто)")
            self.text_area.insert("end", "\n$ ")
            self.text_area.see("end")
            self.root.update_idletasks()
            return True


        self.text_area.insert("end", f"\nОшибка: неизвестная команда '{cmd}'")
        self.text_area.insert("end", "\n$ ")
        self.text_area.see("end")
        self.root.update_idletasks()
        return False


    def run_startup_script(self, script_path):
        script_path = os.path.abspath(os.path.expandvars(script_path))
        if not os.path.isfile(script_path):
            self.text_area.insert("end", f"\nОшибка: файл скрипта не найден: {script_path}\n$ ")
            self.text_area.see("end")
            self.root.update_idletasks()
            return

        self.text_area.insert("end", f"\nВыполнение стартового скрипта: {script_path}\n")
        self.text_area.see("end")
        self.root.update_idletasks()

        with open(script_path, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    self.text_area.insert("end", f"$ {line}\n")
                    self.text_area.see("end")
                    self.root.update_idletasks()
                    continue
                self.text_area.insert("end", f"$ {line}\n")
                self.text_area.see("end")
                self.root.update_idletasks()
                ok = self.execute_command(line, echo_input=False)
                if not ok:
                    self.text_area.insert("end", f"\nСтартовый скрипт остановлен на строке {lineno} из-за ошибки.\n$ ")
                    self.text_area.see("end")
                    self.root.update_idletasks()
                    return
        self.text_area.insert("end", "\nСтартовый скрипт успешно выполнен.\n$ ")
        self.text_area.see("end")
        self.root.update_idletasks()



def parse_args():
    parser = argparse.ArgumentParser(description="Эмулятор VFS")
    parser.add_argument("--vfs", "-v", help="Путь к корню VFS", default=None)
    parser.add_argument("--script", "-s", help="Путь к стартовому скрипту", default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    debug_params = {
        "vfs": args.vfs,
        "script": args.script,
    }
    root = tkinter.Tk()
    Shell(root, vfs_root=args.vfs, startup_script=args.script, debug_params=debug_params)
    root.mainloop()


if __name__ == "__main__":
    main()
