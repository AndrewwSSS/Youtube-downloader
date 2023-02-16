from pytube import YouTube
from pytube.exceptions import PytubeError, VideoUnavailable, RegexMatchError
from colorama import Fore
from stopwatch import Stopwatch
import uuid
import re
import os


def download_video(video_url: str, folder: str):
    timer = Stopwatch().start()

    while True:
        yt = YouTube(video_url)
        title: str
        try:
            title = re.sub(r'[\\:*?"<>/|]', '', yt.title)
        except VideoUnavailable:
            print(Fore.YELLOW + f'Video {video_url} is unavailable')
            break
        except RegexMatchError:
            print(Fore.RED + "Invalid url")
            print(Fore.RED + "Press ENTER to exit ", end='')
            input()
            break
        except PytubeError:
            print(Fore.YELLOW + "Video download failed, retrying")
            continue

        audio_file_name = f'{uuid.uuid1()}.mp4'
        video_file_name = f'{uuid.uuid1()}.mp4'

        # download audio stream
        yt.streams.filter(mime_type="audio/mp4").first().download(folder, audio_file_name)

        # download video stream
        yt.streams.filter(mime_type="video/mp4").order_by('resolution') \
            .desc().first().download(folder, filename=video_file_name)

        audio_file_path = os.path.join(folder, audio_file_name)
        video_file_path = os.path.join(folder, video_file_name)

        # merge two streams
        tmp_file_path = os.path.join(folder, f"{uuid.uuid1()}.mp4")
        cmd = f"ffmpeg -i {audio_file_path} -i {video_file_path} -c:v copy {tmp_file_path} -v error"
        os.system(cmd)

        # clear excess
        os.rename(f"{tmp_file_path}", f"{folder}/{title}.mp4")

        os.remove(audio_file_path)
        os.remove(video_file_path)

        print(Fore.LIGHTYELLOW_EX + title)
        break

    print(Fore.GREEN + f"Video download completed in {timer.tick()}", end='\n\n')
