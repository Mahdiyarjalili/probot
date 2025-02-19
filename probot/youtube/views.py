from django.shortcuts import render
import pytubefix
import requests
from io import BytesIO
from probot.main.credentials import TELEGRAM_API_URL
from probot.main import views as main_views


def download_and_send_video(chat_id, video_url):
    
    

    try:
        video_data  = download_video(video_url)
        video_data.name = "video.mp4"
        send_video(chat_id, video_data)  # Sende das Video

        main_views.send_message(chat_id,'Please enter a valid YouTube video url.')
    except Exception as e:
        main_views.send_message(chat_id, f"Fehler beim Herunterladen des Videos: {e}")
def download_video(video_url):
     try:
        yt = pytubefix.YouTube(video_url)
    
        stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()
        
        if stream:
            # Video in den Arbeitsspeicher (RAM) herunterladen
            video_buffer = BytesIO()
            stream.stream_to_buffer(video_buffer)
            video_buffer.seek(0)  # Zurücksetzen des Dateizeigers auf den Anfang

            # BytesIO-Objekt zurückgeben
            return video_buffer
        else:
            return None
     except Exception as e:
        print(f"Fehler beim Herunterladen des Videos: {e}")
        return None
    
def send_video(chat_id, video_data):
     files = {'video': ('video.mp4',video_data,'video/mp4')}
     data = {'chat_id':chat_id}
     response = requests.post(TELEGRAM_API_URL+"sendVideo", data=data,files=files)

