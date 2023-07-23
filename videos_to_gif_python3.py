#!/usr/bin/python3
# expects to be run as:
# $ python3 videos_to_gif_python3.py video.mp4 subtitles.srt

import os, sys, re, subprocess, shutil, pysrt
from slugify import slugify

gif_dir = "gifs"
filters = "fps=15,scale=600:-1:flags=lanczos"

def striptags(data):
  # I'm a bad person, don't ever do this.
  # Only okay, because of how basic the tags are.
  p = re.compile(r'<.*?>')
  return p.sub('', data)


def makeGif(video, subtitle, start, length, output):
  if not os.path.exists(gif_dir):
    os.makedirs(gif_dir)

  palette = f'{gif_dir}/palette-tmp.png'

  subprocess.call([
    'ffmpeg',
    '-v', 'warning',
    '-i', video,
    '-vf', f'{filters},palettegen=stats_mode=diff',
    palette,
    '-y',
  ])

  subprocess.call([
    'ffmpeg',
    '-v', 'warning',
    '-copyts',
    '-i', video,
    '-i', palette,
    '-lavfi', f'{filters} [x]; [x][1:v] paletteuse=dither=floyd_steinberg,subtitles={subtitle}:force_style=\'fontsize=36,bold=-1,outline=5\'',
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

    print("generating " + gif_filename + "...")
    makeGif(video_file_path, sub_file_path, start, length, gif_filename)

if __name__ == '__main__':
  generateGifs(sys.argv[1], sys.argv[2])
