from pytube import YouTube, Playlist
from pytube.exceptions import PytubeError, VideoUnavailable, RegexMatchError, VideoRegionBlocked
from colorama import Fore
from win32com.shell import shell, shellcon
from threading import *
import os
import time
import re
import math
import uuid
import sys


def download_video(video_url: str, folder: str):
    start = time.time()

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

        print(Fore.LIGHTYELLOW_EX + title)
        break

    # count total time
    diff = (time.time() - start) / 60
    min = int(diff)
    sec = math.ceil((diff - min) * 60)

    print(Fore.GREEN + f"Video download completed in {min}m {sec}s", end='\n\n')


if __name__ == "__main__":
    url = input("Enter video or playlist URL: ")
    download_folder = input("Enter download folder: ")

    if not os.path.exists(download_folder):
        try:
            os.mkdir(download_folder)
        except OSError:
            # get default videos folder
            download_folder = shell.SHGetFolderPath(0, shellcon.CSIDL_MYVIDEO, None, 0)
            print(Fore.YELLOW + "\nDownload folder not found!")
            print(Fore.YELLOW + f"Downloading in default folder: {download_folder}", end='\n\n')

    if 'watch?' in url:  # download video
        download_video(url, download_folder)
        input("Press enter to exit ")
    elif "playlist?" in url:  # download all videos from playlist
        start_time = time.time()

        p = Playlist(url)
        playlist_title: str
        try:
            playlist_title = re.sub(r'[\\:*?"<>/|]', '', p.title)
        except KeyError:
            print(Fore.RED + "Invalid url")
            print(Fore.RED + "Press ENTER to exit ", end='')
            sys.exit()

        print(Fore.YELLOW + f"Start downloading playlist: {playlist_title}")
        download_folder = f"{download_folder}/{playlist_title}"

        if not os.path.exists(download_folder):
            os.mkdir(download_folder)

        progress = 0
        total_count = len(p.video_urls)

        threads_count = 12
        while True:
            threads = []
            if total_count - progress <= threads_count:
                for vid in p.video_urls[progress:total_count]:
                    thread = Thread(target=download_video, args=(vid, download_folder))
                    threads.append(thread)
                    thread.start()

                for thread in threads:
                    thread.join()
                break
            else:
                for vid in p.video_urls[progress:progress+threads_count]:
                    thread = Thread(target=download_video, args=(vid, download_folder))
                    threads.append(thread)
                    thread.start()

                for thread in threads:
                    thread.join()
                progress += threads_count
            print(Fore.GREEN + f"Progress: {int((progress/total_count)*100)}%", end="\n\n")

        difference = (time.time() - start_time) / 60
        min = int(difference)
        sec = math.ceil((difference - min) * 60)

        print(Fore.GREEN + f"Playlist download completed in {min}m {sec}s")
        input(Fore.GREEN + "Press Enter to exit ")
        input()
    else:
        print(Fore.RED + "Invalid url")
        print(Fore.RED + "Press ENTER to exit ", end='')
        input()
