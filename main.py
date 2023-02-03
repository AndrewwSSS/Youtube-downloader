from pytube import YouTube, Playlist, Channel
from colorama import init, Fore
import os
import moviepy.editor as mp
import time
import re
import math


def download_video(url, Download_folder):
    yt = YouTube(url)
    title = re.sub(r'[\\:*?"<>/]', '', yt.title)
    tmp_audio_file = 'unknown_mp3.mp4'
    tmp_video_file = 'unknown_mp4.mp4'

    # download audio stream
    yt.streams.filter(mime_type="audio/mp4").first().download(Download_folder, tmp_audio_file)

    os.chdir(Download_folder)

    # download video stream
    yt.streams.filter(mime_type="video/mp4").order_by('resolution')\
              .desc().first().download(Download_folder, filename=tmp_video_file)

    # merge two streams
    clip = mp.VideoFileClip(tmp_video_file).subclip()
    clip.write_videofile(title + ".mp4", audio=tmp_audio_file, logger=None)

    # clear excess
    os.remove(tmp_audio_file)
    os.remove(tmp_video_file)


if __name__ == "__main__":
    url = input("Enter video or playlist URL: ")
    download_folder = input("Enter download path: ")

    if 'watch?' in url:  # download video
        time_video_start = time.time()
        print(Fore.YELLOW + f"Downloading video...")
        download_video(url, download_folder)

        difference = (time.time() - time_video_start)/60
        total_video_min = int(difference)
        total_video_sec = math.ceil((difference - total_video_min) * 60)

        print(Fore.GREEN + f"Video download completed in {total_video_min}m {total_video_sec}s", end='\n\n')
    elif "playlist?" in url:  # download all videos from playlist
        p = Playlist(url)
        playlist_title = p.title
        start_time = time.time()
        print(Fore.YELLOW + f"Start downloading playlist {playlist_title}")
        download_folder = f"{download_folder}/{playlist_title}"
        os.mkdir(download_folder)

        progress = 0
        total_count = len(p.video_urls)
        for video in p.videos:
            time_video_start = time.time()
            print(Fore.YELLOW + f"Downloading video {video.title}...")

            # try:

            download_video(video.watch_url, download_folder)
            progress += 1

            difference = (time.time() - time_video_start) / 60
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
#         time_video_start = time.time()
#         print(f"Downloading video {video.title}...")
#         download_video(video.watch_url, download_folder)
#         progress += 1
#         total_video_time = format(((time.time() - time_video_start)/60), '.2f')
#         print(f"Downloading video complete in {total_video_time}m", end='\n')
#         print(f"Current progress: {progress}/{total_count}")
#
#     total_playlist_time = float('{.2f}'.format((time.time()-time_channel_start)/60))
#     print(f"Downloading videos from channel complete in {total_playlist_time}m")
