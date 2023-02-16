from pytube import Playlist
from colorama import Fore
from win32com.shell import shell, shellcon
from threading import Thread
from lib import download_video
from stopwatch import Stopwatch
import os
import re
import sys


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
        playlist_timer = Stopwatch().start()

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

        print(Fore.GREEN + f"Playlist download completed in {playlist_timer.tick()}")
        input(Fore.GREEN + "Press Enter to exit ")
    else:
        print(Fore.RED + "Invalid url")
        input(Fore.RED + "Press ENTER to exit ")

