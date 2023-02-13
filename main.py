from pytube import YouTube, Playlist
from  pytube.exceptions import PytubeError
from colorama import Fore
from win32com.shell import shell, shellcon
from threading import *
import os
import time
import re
import math
import uuid


def aboba(video_url, download_folder):
    time_start = time.time()

    while True:
        try:
            # print(Fore.YELLOW + f"Downloading video {video_url}")
            download_video(video_url, download_folder)
            break
        except PytubeError:
            # print(Fore.RED + "[Debug] Download error. Retry...", end='\n\n')
            continue

    difference = (time.time() - time_start) / 60
    min = int(difference)
    sec = math.ceil((difference - min) * 60)

    print(Fore.GREEN + f"Video download completed in {min}m {sec}s")


def download_video(video_url, download_folder):

    yt = YouTube(video_url)

    title = re.sub(r'[\\:*?"<>/|]', '', yt.title)
    downloading_sources = time.time()
    audio_file = f'{uuid.uuid1()}.mp4'
    video_file = f'{uuid.uuid1()}.mp4'

    # download audio stream
    yt.streams.filter(mime_type="audio/mp4").first().download(download_folder, audio_file)

    # download video stream

    yt.streams.filter(mime_type="video/mp4").order_by('resolution') \
        .desc().first().download(download_folder, filename=video_file)
    time_difference = (time.time() - downloading_sources) / 60

    minutes = int(time_difference)
    seconds = math.ceil((time_difference - minutes) * 60)
    # print(Fore.LIGHTYELLOW_EX + f"[DEBUG] Download sources completed in {minutes}m {seconds}s")

    merge_time = time.time()

    # merge two streams
    file_name = uuid.uuid1()
    cmd = f"ffmpeg -i {download_folder}/{audio_file} -i {download_folder}/{video_file} -c:v copy {download_folder}/{file_name}.mp4 -v error"
    os.system(cmd)

    # clear excess
    os.rename(f"{download_folder}/{file_name}.mp4", f"{download_folder}/{title}.mp4")

    os.remove(f"{download_folder}/{audio_file}")
    os.remove(f"{download_folder}/{video_file}")

    time_difference = (time.time() - merge_time) / 60
    minutes = int(time_difference)
    seconds = math.ceil((time_difference - minutes) * 60)
    print(Fore.LIGHTYELLOW_EX + f"[DEBUG] " + title)
    # print(Fore.LIGHTYELLOW_EX + f"[DEBUG] Merge completed in {minutes}m {seconds}s")


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

        difference = (time.time() - time_start) / 60
        min = int(difference)
        sec = math.ceil((difference - min) * 60)

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
                    threads.append(Thread(target=aboba, args=(vid, download_folder)))
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join()
                break
            else:
                threads = []
                for vid in p.video_urls[progress:progress+threads_count]:
                    threads.append(Thread(target=aboba, args=(vid, download_folder)))
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join()
                progress += threads_count

        difference = (time.time() - start_time) / 60
        min = int(difference)
        sec = math.ceil((difference - min) * 60)

        print(f"Playlist download completed in {min}m {sec}s")
        input("Press Enter to exit")
