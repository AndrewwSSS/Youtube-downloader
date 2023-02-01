from pytube import YouTube, Playlist, Channel
import os
import moviepy.editor as mp
import time
import re

def download_video(Url, Download_folder):
    yt = YouTube(Url)
    title = re.sub(r'[\\:*?"<>]', '', yt.title)
    audiofile_name = 'unknown_mp3.mp4'
    moviefile_name = 'unknown_mp4.mp4'

    # download audio stream
    yt.streams.filter(mime_type="audio/mp4").first().download(Download_folder, audiofile_name)

    os.chdir(Download_folder)

    # download video stream
    yt.streams.filter(mime_type="video/mp4").order_by('resolution').desc().first().download(Download_folder, filename=moviefile_name)

    # merge two streams
    clip = mp.VideoFileClip(moviefile_name).subclip()
    clip.write_videofile(title + ".mp4", audio=audiofile_name, logger=None, )

    # clear excess
    os.remove(audiofile_name)
    os.remove(moviefile_name)


url = input("Enter video or playlist URL: ")
download_folder = input("Enter download path: ")
print("\n")


if('watch?' in url):  # download video
    time_video_start = time.time()
    print(f"Downloading video...")
    download_video(url, download_folder)
    total_video_time = format(((time.time() - time_video_start) / 60), '.2f')
    print(f"Downloading video complete in {total_video_time}m", end='\n\n')
elif("playlist?" in url):  #download all videos from playlist
    p = Playlist(url)
    playlist_title = p.title
    time_playlist_start = time.time()
    print(f"Start downloading playlist {playlist_title}")
    download_folder = f"{download_folder}/{playlist_title}"
    os.mkdir(download_folder)

    progress = 0
    total_count = len(p.video_urls)
    for video in p.videos:
        time_video_start = time.time()
        print(f"Downloading video {video.title}...")
        try:
            download_video(video.watch_url, download_folder)
            progress += 1
            total_video_time = format(((time.time() - time_video_start) / 60), '.2f')
            print(f"Downloading video complete in {total_video_time}m")
            print(f"Total progress: {progress}/{total_count}", end='\n\n')
        except:
            print("Downloading error")
            continue

    total_playlist_time = format((time.time()-time_playlist_start)/60, '.2f')
    print(f"Downloading playlist complete in {total_playlist_time}m")


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



