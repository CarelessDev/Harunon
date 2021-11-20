import os

song_lists = [
    x.split(".")[0]
    for x in os.listdir("歌詞") if x.endswith(".haruno")
]
