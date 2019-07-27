import youtube_dl

ydl_opts = {
    'format': 'bestaudio/best',
    # 'playlist_items': 'true',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp4',
        'preferredquality': '192',
    }],
}
with youtube_dl.YoutubeDL(params=ydl_opts) as ydl:
    ydl.download(['https://v.qq.com/x/cover/r70bh0e2i2il1l4/j0019td4tgy.html'])
