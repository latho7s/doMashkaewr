import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import zipfile
import json
import sys
import argparse

class ShellEmulator:
    def __init__(self, master, config):
        self.master = master
        self.master.title("Shell Emulator")
        self.current_path = "/"
        self.history = []

        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.username = config['username']
        self.virtual_fs_path = config['virtual_fs']
        self.start_script = config.get('start_script')

        self.label = tk.Label(master, text=f"{self.username}")
        self.label.pack(padx=10, pady=5)

        self.entry = tk.Entry(master)
        self.entry.pack(padx=10, pady=10, fill=tk.X)
        self.entry.bind("<Return>", self.execute_command)

        # Проверка существования виртуальной файловой системы
        if not os.path.exists(self.virtual_fs_path):
            messagebox.showerror("Ошибка", "Файл виртуальной файловой системы не найден.")
            sys.exit(1)

        # Распаковка виртуальной файловой системы при запуске
        self.extract_virtual_fs()

        # Загрузка стартового скрипта, если указан
        if self.start_script:
            self.load_script(self.start_script)

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(description='Запуск эмулятора командной строки.')
        parser.add_argument('config', type=str, help='Путь к конфигурационному файлу (JSON).')
        
        args = parser.parse_args()
        
        if not os.path.exists(args.config):
            parser.error(f"Файл конфигурации '{args.config}' не найден.")
        
        return args

    def extract_virtual_fs(self):
        with zipfile.ZipFile(self.virtual_fs_path) as zip_ref:
            zip_ref.extractall("virtual_fs")

    def load_script(self, script_file):
        try:
            with open(script_file, 'r') as file:
                for line in file:
                    command = line.strip()
                    if command:  
                        self.execute_command_from_script(command)
        except FileNotFoundError:
            messagebox.showerror("Ошибка", f"Файл скрипта {script_file} не найден.")

    def execute_command(self, event):
        command = self.entry.get()
        self.history.append(command)

        command_dict = {
            "ls": self.list_files,
            "cd": lambda: self.change_directory(command[3:]),
            "pwd": self.print_working_directory,
            "cat": lambda: self.cat_file(command[4:]),
            "exit": self.master.quit,
            "history": self.show_history,
            "tac": lambda: self.tac_file(command[5:]),
            "du": lambda: self.du(command[3:])
        }

        cmd_func = command_dict.get(command.split()[0], None)

        if cmd_func:
            cmd_func()
        else:
            self.text_area.insert(tk.END, f"{self.username}: команда не найдена\n")

        self.entry.delete(0, tk.END)

    def execute_command_from_script(self, command):
        command_dict = {
            "ls": self.list_files,
            "cd": lambda: self.change_directory(command[3:]),
            "pwd": self.print_working_directory,
            "cat": lambda: self.cat_file(command[4:]),
            "exit": self.master.quit,
            "history": self.show_history,
            "tac": lambda: self.tac_file(command[5:]),
            "du": lambda: self.du(command[3:])
        }

        cmd_func = command_dict.get(command.split()[0], None)

        if cmd_func:
            cmd_func()
        else:
            self.text_area.insert(tk.END, f"{self.username}: команда не найдена\n")

    def list_files(self):
        try:
            files = os.listdir(f"virtual_fs{self.current_path}")
            output = "\n".join(files) if files else "Пустая директория\n"
            self.text_area.insert(tk.END, f"{output}\n")
        except FileNotFoundError:
            self.text_area.insert(tk.END, "Директория не найдена\n")

    def change_directory(self, path):
        if path == "..":
            if self.current_path != "/":
                parts = self.current_path.split("/")
                parts.pop()  
                self.current_path = "/".join(parts) or "/"
                return
        
        new_path = os.path.join(f"virtual_fs{self.current_path}", path)
        
        if os.path.isdir(new_path):
            self.current_path = new_path.replace("virtual_fs", "")
            return
        else:
            self.text_area.insert(tk.END, "Директория не найдена\n")

    def print_working_directory(self):
        current_dir = f"{self.username}:{self.current_path}\n"
        self.text_area.insert(tk.END, current_dir)

    def cat_file(self, filename):
        try:
            with open(os.path.join(f"virtual_fs{self.current_path}", filename.strip()), 'r') as file:
                content = file.read()
                self.text_area.insert(tk.END, f"{content}\n")
        except FileNotFoundError:
            self.text_area.insert(tk.END, "Файл не найден\n")

    def tac_file(self, filename):
        try:
            file_path = os.path.join(f"virtual_fs{self.current_path}", filename.strip())
            with open(file_path, 'r') as file:
                content = file.readlines()[::-1]
                output = ''.join(content)
                self.text_area.insert(tk.END, f"{output}\n")
        except FileNotFoundError:
            self.text_area.insert(tk.END, "Файл не найден\n")

    def du(self, path):
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(os.path.join("virtual_fs", path.strip())):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
            
            size_in_kb = total_size / 1024  # Размер в КБ
            output = f"Размер директории '{path.strip()}': {size_in_kb:.2f} KB\n"
            self.text_area.insert(tk.END, output)
        
        except FileNotFoundError:
            self.text_area.insert(tk.END, "Директория не найдена\n")

    def show_history(self):
        history_output = "\n".join(self.history) or "История пуста\n"
        self.text_area.insert(tk.END, f"История команд:\n{history_output}\n")


if __name__ == "__main__":
    args = ShellEmulator.parse_arguments()
    
    with open(args.config) as config_file:
        config = json.load(config_file)

    root = tk.Tk()
    app = ShellEmulator(root, config)
    
    root.mainloop()
