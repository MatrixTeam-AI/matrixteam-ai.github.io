import argparse
import os
import json
parser = argparse.ArgumentParser()
parser.add_argument("--json","-j", type=str)
parser.add_argument("--output","-o", type=str, default="./test_output.txt")
args = parser.parse_args()
template = """
    <div class="tiling-video-outer">
      <div class="tiling-video-container">
        <video preload="none" poster="videos_icon/{}" onclick="toggleVideoPlay(this)" class="tiling-video" loop>
          <source src="videos/{}" type="video/mp4" />
        </video>
        <div class="tiling-prompt">
        <div>{}</div>
        </div>
      </div>
    </div>
"""
objs = json.loads(open(args.json, "r").read())
f = open(args.output, "w")
for obj in objs:
    video_name = obj["video"].split("/")[-1]
    video_prompt = obj["prompt"]
    img_name = video_name.replace("processed", "img").replace("mp4","png")
    f.write(template.format(img_name, video_name, video_prompt))

f.close()
