from mutagen.easyid3 import EasyID3
import logging
from vkpymusic import  TokenReceiver,Service
import dotenv
import os
import sys
import argparse

LOG_FORMAT = logging.Formatter(u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s')
LOG_FILENAME = "bot.log"
LOG_LEVEL = logging.WARN

download_path = "C:\\Users\\User\\Music\\Dl\\"


def _setup_logger() -> logging.Logger:
    file_handler = logging.FileHandler(LOG_FILENAME,encoding="utf-8")
    file_handler.setFormatter(LOG_FORMAT)
    file_handler.setLevel(LOG_LEVEL)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(LOG_FORMAT)
    console_handler.setLevel(LOG_LEVEL)

    bot_logger = logging.getLogger('bot')
    bot_logger.setLevel(LOG_LEVEL)
    bot_logger.addHandler(file_handler)
    bot_logger.addHandler(console_handler)
    return bot_logger

def load_env(path : str = None):
    dotenv.load_dotenv()
    env = dotenv.dotenv_values()
    return env

def search(query, count = 10):
    env = load_env()
    service = Service.parse_config()
    service.set_logger(_setup_logger())
    if  service is None or not service.is_token_valid():
        token_reciever = TokenReceiver(env["VK_LOGIN"],env["VK_PASS"])
        if token_reciever.auth():
            token_reciever.get_token()
            token_reciever.save_to_config()
        else:
            print("Check your credentials")
            exit(-1)
        service = Service.parse_config()

    songs = service.search_songs_by_text(query,count = count)
    if songs is None:
        print("No songs :(")
        exit(-2)
    for i,song in enumerate(songs,1):
        print(f"""{i}) {song.title}—{song.artist} ({song.duration//60}:{song.duration%60:02})""")
        print(song.artist)


    n = int(input("Enter num of song: "))-1
    song = songs[n]
    title  = song.title
    artist = song.artist
    temp_audio_path = service.save_music(song)
    audio = EasyID3(temp_audio_path)
    audio["title"] = title
    audio["artist"] = artist
    audio.save()
    print(artist)
    os.replace(temp_audio_path,f"{download_path}{title}—{artist}.mp3")

    os.replace(temp_audio_path,f"{env['PATH']}{title}—{artist}.mp3")




if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query",nargs = "+", default = "test_music",type=str)
    parser.add_argument("-n", nargs=1, default="10", type=int)
    args = parser.parse_args()

    query_str = " ".join(args.query)
    search(query_str,args.n)