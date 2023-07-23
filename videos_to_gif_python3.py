#!/usr/bin/python3
# expects to be run as:
# $ python3 videos_to_gif_python3.py video.mp4 subtitles.srt

import os, sys, re, subprocess, pysrt, itertools, json
from slugify import slugify

fps = 15
width = 800
fontsize = 36
outline = 5

skip_patterns = [
  r".*\.\.\.$",
  r".*\,$",
  r".*[a-z]$",
  r"^[a-z].*",
]

no_skips = lambda y: len(list(itertools.filterfalse(
  lambda x: re.search(x, y.text), skip_patterns
))) == len(skip_patterns)

gif_dir = "gifs"

def striptags(data):
  # I'm a bad person, don't ever do this.
  # Only okay, because of how basic the tags are.
  p = re.compile(r'<.*?>')
  return p.sub('', data)


def makeGif(video, subtitle, start, length, output):
  if not os.path.exists(gif_dir):
    os.makedirs(gif_dir)

  args = [
    'ffmpeg',
    '-v', 'error',
    '-copyts',
    '-i', video,
    '-lavfi', f"fps={15},scale={width}:-1,subtitles='{subtitle}':force_style=\'fontsize={fontsize},bold=-1,outline={outline}'",
    '-ss', start,
    '-t', length,
    output,
    '-y', # y is for yolo
  ]

  print(' '.join(args))
  subprocess.call(args)


def generateGifs(video_file_path, sub_file_path):
  outpath = "gifs"

  subs = pysrt.open(sub_file_path, encoding="utf-8")
  filtered_subs = list(filter(no_skips, subs))

  metadata = []

  # generate a gif for every line of dialogue
  for i, sub in enumerate(filtered_subs):
    # 00:00:00,000 => 00:00:00.000
    start = str(sub.start).replace(',', '.')
    length = str(sub.end - sub.start).replace(',', '.')

    gif_filename = os.path.join(outpath, f'{i:06}-{slugify(striptags(sub.text))}.gif')
    metadata.append(json.dumps({ 'text': sub.text, 'path': gif_filename }))

    print(f"Generating {gif_filename}")
    makeGif(video_file_path, sub_file_path, start, length, gif_filename)
    with open(os.path.join(outpath, "metadata.json"), "w") as f:
      f.write(f"[{(',').join(metadata)}]")


if __name__ == '__main__':
  generateGifs(sys.argv[1], sys.argv[2])
