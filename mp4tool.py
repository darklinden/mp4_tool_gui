#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
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
    print(' '.join(cmd))

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output, err = process.communicate()
    exit_code = process.returncode

    return exit_code == 0, err, output


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
    des_log = value[:-len(tmp_ext) - 1] + '_out.log'

    probe_cmd = 'ffprobe'
    if platform.system() == 'Windows':
        probe_cmd = 'ffprobe.exe'
        works, e, eo = run_cmd([probe_cmd, '-version'])
        if not works:
            probe_cmd = 'ffmpeg/bin/ffprobe.exe'

    mpeg_cmd = 'ffmpeg'
    if platform.system() == 'Windows':
        mpeg_cmd = 'ffmpeg.exe'
        works, e, eo = run_cmd([mpeg_cmd, '-version'])
        if not works:
            mpeg_cmd = 'ffmpeg/bin/ffmpeg.exe'

    if os.path.exists(des_file):
        os.remove(des_file)

    if os.path.exists(des_log):
        os.remove(des_log)

    success, e, out = run_cmd(
        [probe_cmd, '-v', 'error', '-show_entries', 'stream=width,height', '-of', 'json', value])
    # b'{    "programs": [    ],    "streams": [        {            "width": 720,            "height": 406        },        {        }    ]}'

    w = 0
    h = 0
    if success:
        try:
            out = out.decode("utf-8").replace('\\n', '')
            js = json.loads(out)
            w = int(js['streams'][0]['width'])
            h = int(js['streams'][0]['height'])
        except:
            pass

    if w > h:
        if w > 720:
            scale = 'scale=720:-2'
        else:
            scale = 'scale=' + str(w) + ':-2'
    else:
        if h > 720:
            scale = 'scale=-2:720'
        else:
            scale = 'scale=-2:' + str(h) + ''

    success, err, err_out = run_cmd(
        [mpeg_cmd, '-i', value, '-vcodec', 'libx264', '-crf', '20', '-filter:v', scale, '-c:a', 'copy',
         des_file])

    if success:
        messagebox.showinfo(title=None, message='已压缩')
        show_list()
    else:
        with open(des_log, 'w') as f:
            f.write(str(err))
            f.write('\n\n')
            f.write(str(err_out))
            f.close()

        messagebox.showinfo(title=None, message='压缩失败')


def show_list():
    list_box.delete(0, END)
    for (dir_path, _, file_names) in os.walk(working_path):
        for f in file_names:
            abs_path = os.path.join(dir_path, f)
            tmp_ext = abs_path.split('.')[-1]
            if tmp_ext.lower() == 'mp4' or tmp_ext.lower() == 'mov':
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
