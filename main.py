from pytube import YouTube, Playlist
from pytube.exceptions import PytubeError, VideoUnavailable
from colorama import Fore
from win32com.shell import shell, shellcon
from threading import *
import os
import time
import re
import math
import uuid
from datetime import datetime


def download_video(video_url: str, folder: str):
    start = time.time()

    while True:
        try:
            yt = YouTube(video_url)

            title = re.sub(r'[\\:*?"<>/|]', '', yt.title)
            downloading_sources = time.time()
            audio_file = f'{uuid.uuid1()}.mp4'
            video_file = f'{uuid.uuid1()}.mp4'

            # download audio stream
            yt.streams.filter(mime_type="audio/mp4").first().download(folder, audio_file)

            # download video stream
            yt.streams.filter(mime_type="video/mp4").order_by('resolution') \
                .desc().first().download(folder, filename=video_file)

            # merge two streams
            file_name = uuid.uuid1()
            cmd = f"ffmpeg -i {folder}/{audio_file} -i {folder}/{video_file} -c:v copy {folder}/{file_name}.mp4 -v error"
            os.system(cmd)

            # clear excess
            os.rename(f"{folder}/{file_name}.mp4", f"{folder}/{title}.mp4")

            os.remove(f"{folder}/{audio_file}")
            os.remove(f"{folder}/{video_file}")

            print(Fore.LIGHTYELLOW_EX + f"[DEBUG] " + title)
            break
        except VideoUnavailable:
            print(Fore.RED + f'Video {video_url} is unavaialable, skipping.')
            break
        except PytubeError:
            continue


    diff = (time.time() - start) / 60
    min = int(diff)
    sec = math.ceil((diff - min) * 60)

    print(Fore.GREEN + f"Video download completed in {min}m {sec}s")


if __name__ == "__main__":
    url = input("Enter video or playlist URL: ")
    download_folder = input("Enter download folder: ")

    if not os.path.exists(download_folder):
        video_folder = shell.SHGetFolderPath(0, shellcon.CSIDL_MYVIDEO, None, 0)
        download_folder = video_folder
        print(Fore.RED + "Download folder not found!")
        print(Fore.RED + f"Downloading in default folder: {video_folder}", end='\n\n')

    if 'watch?' in url:  # download video
        time_start = time.time()

        while True:
            print(Fore.YELLOW + f"Downloading video...")
            try:
                download_video(url, download_folder)
                break
            except PytubeError:
                print(Fore.RED + "[Debug] Download error. Retry...", end='\n\n')
                continue

        diff = (time.time() - time_start) / 60
        min = int(diff)
        sec = math.ceil((diff - min) * 60)

        print(Fore.GREEN + f"Video download completed in {min}m {sec}s", end='\n\n')
        input()
    elif "playlist?" in url:  # download all videos from playlist
        p = Playlist(url)
        playlist_title = re.sub(r'[\\:*?"<>/|]', '', p.title)
        start_time = time.time()

        print(Fore.YELLOW + f"Start downloading playlist {playlist_title}")

        download_folder = f"{download_folder}/{playlist_title}"

        if not os.path.exists(download_folder):
            os.mkdir(download_folder)

        progress = 0
        total_count = len(p.video_urls)

        threads_count = 16
        while True:
            if total_count - progress <= threads_count:
                threads = []
                for vid in p.video_urls[progress:total_count]:
                    thread = Thread(target=download_video, args=(vid, download_folder))
                    threads.append(thread)
                    thread.start()

                for thread in threads:
                    thread.join()
                break
            else:
                threads = []
                for vid in p.video_urls[progress:progress+threads_count]:
                    thread = Thread(target=download_video, args=(vid, download_folder))
                    threads.append(thread)
                    thread.start()

                for thread in threads:
                    thread.join()
                progress += threads_count

        difference = (time.time() - start_time) / 60
        min = int(difference)
        sec = math.ceil((difference - min) * 60)

        print(f"Playlist download completed in {min}m {sec}s")
        input("Press Enter to exit")
