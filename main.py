#!/usr/bin/env python3
# script to generate a timelapse

import os
import subprocess
import sys

from tempfile import NamedTemporaryFile
from PIL import Image


def constant_speed_video(nfile, length, frate):
    # > 1, skip some frames; < 1, repeat some frames
    speedup =  length and nfile / frate * length or 1

    nframes = 0
    total_frames = length and length*frate or nfile
    progress_frames = nframes / total_frames
    for i in range(nfile):
        progress_file_list = i / nfile

        while progress_file_list >= progress_frames:
            nframes += 1
            progress_frames = nframes / total_frames
            yield i


def generate_concat_file(file_list, output, length=False, frate=25):
    """ Generate the list of commands for ffmepg
    file_list: list of path to files
    output: buffer to write commands
    length: number of seconds of expected video
    frate: frame rate of the video
    """
    for file_index in constant_speed_video(len(file_list), length, frate):
        output.write("file %s\n" % file_list[file_index].__repr__())

def render_video(command_filename, output_filename='output.avi', frate=25):
    subprocess.call([
        'ffmpeg', '-r', str(frate), '-f', 'concat', '-i', command_filename, '-c:v', 'copy', output_filename
    ])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Specify name of folder containing the images")
    else:
        SRC_DIR = sys.argv[1]
        file_list = []
        for f in os.listdir(SRC_DIR):
            path = os.path.join(SRC_DIR, f)
            try:
                Image.open(path)
                file_list.append(path)
            except IOError:
                pass
        file_list.sort()

        with NamedTemporaryFile('w') as tempf:
            generate_concat_file(file_list, tempf, length=5)
            tempf.flush()
            render_video(tempf.name)
