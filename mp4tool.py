#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import platform
import subprocess
from tkinter import *
from tkinter import messagebox

global list_box
global working_path


def make_window(working_path):
    window = Tk()
    window.geometry('480x640')
    window.title(working_path)
    return window


def make_list(window):
    global list_box
    frame = Frame(window)
    frame.pack(side=TOP, fill=BOTH, expand=TRUE)

    list_box = Listbox(frame, font=("Helvetica", 12))
    list_box.pack(side=LEFT, fill=BOTH, expand=TRUE)

    scrollbar = Scrollbar(frame, orient="vertical")
    scrollbar.config(command=list_box.yview)
    scrollbar.pack(side=RIGHT, fill=Y)

    list_box.config(yscrollcommand=scrollbar.set)


def run_cmd(cmd):
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    err_output, err = process.communicate()
    exit_code = process.returncode

    if exit_code != 0:
        if err is not None:
            messagebox.showinfo(title=None, message=err)

    return exit_code == 0


def clicked():
    value = None

    try:
        selection = list_box.curselection()
        value = list_box.get(selection[0])
    except:
        pass

    if not value or value is None:
        messagebox.showinfo(title=None, message='请先选择文件')
        return

    tmp_ext = value.split('.')[-1]
    des_file = value[:-len(tmp_ext) - 1] + '_out.' + tmp_ext

    cmd = 'ffmpeg'
    if platform.system() == 'Windows':
        cmd = 'ffmpeg/bin/ffmpeg.exe'

    success = run_cmd(
        [cmd, '-i', value, '-vcodec', 'libx264', '-crf', '20', '-filter:v', 'scale=720:-1', '-c:a', 'copy', des_file])

    if success:
        messagebox.showinfo(title=None, message='已压缩')
        show_list()


def show_list():
    list_box.delete(0, END)
    for (dir_path, _, file_names) in os.walk(working_path):
        for f in file_names:
            abs_path = os.path.join(dir_path, f)
            tmp_ext = abs_path.split('.')[-1]
            if tmp_ext == 'mp4':
                list_box.insert(END, abs_path)


def show_btns(window):
    frame = Frame(window)
    frame.pack(side=BOTTOM, fill=X, expand=FALSE)

    Button(frame, text="刷新", command=show_list).pack(side=LEFT, expand=TRUE)
    Button(frame, text="压缩", command=clicked).pack(side=RIGHT, expand=TRUE)


def main():
    global working_path
    working_path = os.path.abspath(__file__)
    working_path = os.path.dirname(working_path)
    # print('working_path: ' + working_path)

    window = make_window(working_path)

    make_list(window)

    show_list()

    show_btns(window)

    window.mainloop()


if __name__ == '__main__':
    main()
