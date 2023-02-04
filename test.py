import os
cmd = f"ffmpeg  -i E:/unknown_mp3.mp4 -i E:/unknown_mp4.mp4 -c:v  copy E:/1.mp4 -v error"
os.system(cmd)

