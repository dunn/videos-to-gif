#!/usr/bin/python3
# expects to be run as:
# $ python3 videos_to_gif_python3.py video.mp4 subtitles.srt

import os, sys, re, subprocess, shutil, pysrt, itertools
from slugify import slugify

skip_patterns = [
  r".*\.\.\.$",
  r"^[a-z].*",
]

gif_dir = "gifs"

def striptags(data):
  # I'm a bad person, don't ever do this.
  # Only okay, because of how basic the tags are.
  p = re.compile(r'<.*?>')
  return p.sub('', data)


def makeGif(video, subtitle, start, length, output):
  if not os.path.exists(gif_dir):
    os.makedirs(gif_dir)

  subprocess.call([
    'ffmpeg',
    '-v', 'error',
    '-copyts',
    '-i', video,
    '-lavfi', f'fps=15,scale=800:-1,subtitles=\'{subtitle}\':force_style=\'fontsize=36,bold=-1,outline=5\'',
    '-ss', start,
    '-t', length,
    output,
    '-y', # y is for yolo
  ])


def generateGifs(video_file_path, sub_file_path):
  outpath = "gifs"

  subs = pysrt.open(sub_file_path, encoding="utf-8")

  # generate a gif for every line of dialogue
  for i, sub in enumerate(subs):
    # 00:00:00,000 => 00:00:00.000
    start = str(sub.start).replace(',', '.')
    length = str(sub.end - sub.start).replace(',', '.')

    gif_filename = os.path.join(outpath, f'{i:06}-{slugify(striptags(sub.text))}.gif')

    # this is stupid
    if len(list(itertools.filterfalse(lambda x: re.search(x, sub.text), skip_patterns))) != len(skip_patterns):
      next
    else:
      print("generating " + gif_filename + "...")
      makeGif(video_file_path, sub_file_path, start, length, gif_filename)

if __name__ == '__main__':
  generateGifs(sys.argv[1], sys.argv[2])
