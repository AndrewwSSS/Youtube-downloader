from pytube import YouTube, Playlist, Channel
from colorama import init, Fore
import os
# import moviepy.editor as mp
import time
import re
import math


def download_video(video_url, download_folder):
    yt = YouTube(video_url)
    title = re.sub(r'[\\:*?"<>/|]', '', yt.title)
    downloading_sources = time.time()
    audio_file = 'unknown1.mp4'
    video_file = 'unknown2.mp4'

    # download audio stream
    yt.streams.filter(mime_type="audio/mp4").first().download(download_folder, audio_file)

    # download video stream
    yt.streams.filter(mime_type="video/mp4").order_by('resolution') \
        .desc().first().download(download_folder, filename=video_file)

    time_difference = (time.time() - downloading_sources) / 60
    minutes = int(time_difference)
    seconds = math.ceil((time_difference - minutes) * 60)
    print(Fore.GREEN + f"[DEBUG] Download sources completed in {minutes}m {seconds}s")

    merge_time = time.time()

    # merge two streams

    cmd = f"ffmpeg -i {download_folder}/{audio_file} -i {download_folder}/{video_file} -c:v copy {download_folder}/123result123.mp4 -v error"
    os.system(cmd)

    # clear excess

    os.chdir(download_folder)
    os.rename(f"123result123.mp4", f"{title}.mp4")

    os.remove(audio_file)
    os.remove(video_file)

    time_difference = (time.time() - merge_time) / 60
    minutes = int(time_difference)
    seconds = math.ceil((time_difference - minutes) * 60)
    print(Fore.GREEN + f"[DEBUG] Merge completed in {minutes}m {seconds}s")


if __name__ == "__main__":
    url = input("Enter video or playlist URL: ")
    download_folder = input("Enter download folder: ")

    if not os.path.exists(download_folder):
        print(Fore.RED + "Folder not found!")
        input()
        exit()

    if 'watch?' in url:  # download video
        time_start = time.time()
        print(Fore.YELLOW + f"Downloading video")
        download_video(url, download_folder)

        difference = (time.time() - time_start) / 60
        total_video_min = int(difference)
        total_video_sec = math.ceil((difference - total_video_min) * 60)

        print(Fore.GREEN + f"Video download completed in {total_video_min}m {total_video_sec}s", end='\n\n')
    elif "playlist?" in url:  # download all videos from playlist
        p = Playlist(url)
        playlist_title = re.sub(r'[\\:*?"<>/|]', '', p.title)
        start_time = time.time()
        print(Fore.YELLOW + f"Start downloading playlist {playlist_title}")
        download_folder = f"{download_folder}/{playlist_title}"
        os.mkdir(download_folder)

        progress = 0
        total_count = len(p.video_urls)
        for video in p.videos:
            time_start = time.time()
            print(Fore.YELLOW + f"Downloading video {video.title}...")

            # try:

            download_video(video.watch_url, download_folder)
            progress += 1

            difference = (time.time() - time_start) / 60
            total_video_min = int(difference)
            total_video_sec = math.ceil((difference - total_video_min) * 60)

            print(Fore.GREEN + f"Video download completed in {total_video_min}m {total_video_sec}s")
            print(Fore.GREEN + f"Total progress: {progress}/{total_count}", end='\n\n')

            # except PytubeError:
            #     print(Fore.RED + "! Downloading error !")
            #     continue

        difference = (time.time() - start_time) / 60
        total_video_min = int(difference)
        total_video_sec = math.ceil((difference - total_video_min) * 60)

        print(f"Playlist download completed in {total_video_min}m {total_video_sec}s")

# elif('@' in url):  #download all videos from channel
#     c = Channel(url)
#     channel_title = c.title
#     time_channel_start = time.time()
#     print(f"Start downloading all videos from {channel_title}")
#     download_folder = f"{download_folder}/{channel_title}"
#     os.mkdir(download_folder)
#
#     progress = 0
#     total_count = len(c.video_urls)
#     for video in c.videos:
#         time_start = time.time()
#         print(f"Downloading video {video.title}...")
#         download_video(video.watch_url, download_folder)
#         progress += 1
#         total_video_time = format(((time.time() - time_start)/60), '.2f')
#         print(f"Downloading video complete in {total_video_time}m", end='\n')
#         print(f"Current progress: {progress}/{total_count}")
#
#     total_playlist_time = float('{.2f}'.format((time.time()-time_channel_start)/60))
#     print(f"Downloading videos from channel complete in {total_playlist_time}m")
