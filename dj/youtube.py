import youtube_dl
import os.path

outdir = "/var/django/DJ_Ango/dj/songs/"
ydl = youtube_dl.YoutubeDL({'outtmpl': outdir + '%(title)s(%(id)s).%(ext)s',
                            'format': 'bestaudio',
                            'quiet': True,
                            'restrictfilenames': True})
ydl.add_default_info_extractors()

def download_audio(ytid):
  result = ydl.extract_info('http://www.youtube.com/watch?v=' + ytid,
                            download=False)
  if 'entries' in result:
      video = result['entries'][0]
  else:
      video = result
  info = ydl.process_video_result(video)
  info["filename"] = os.path.basename(ydl.prepare_filename(info))
  return info
