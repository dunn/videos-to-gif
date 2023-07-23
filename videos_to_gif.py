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
    # we're rounding the milliseconds to the nearest frame to avoid descyncs
    # with the subtitles
    frame_chunk = 1000 / fps

    start = sub.start
    start_ms = start.milliseconds
    start.milliseconds = start_ms + (frame_chunk - (start_ms % frame_chunk))

    end = sub.end
    end_ms = end.milliseconds
    end.milliseconds = end_ms - (end_ms % frame_chunk)

    start_str = str(start).replace(',', '.')
    length_str = str(end - start).replace(',', '.')


    gif_filename = os.path.join(outpath, f'{i:06}-{slugify(striptags(sub.text))}.gif')
    metadata.append(json.dumps({ 'text': sub.text, 'path': gif_filename }))

    makeGif(video_file_path, sub_file_path, start_str, length_str, gif_filename)
    with open(os.path.join(outpath, "metadata.json"), "w") as f:
      f.write(f"[{(',').join(metadata)}]")


if __name__ == '__main__':
  generateGifs(sys.argv[1], sys.argv[2])
