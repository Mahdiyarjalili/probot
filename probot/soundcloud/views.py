from django.shortcuts import render
import subprocess
import requests
import os
import io
import re
from probot.main.credentials import TELEGRAM_API_URL

def download_soundcloud(chat_id,message_id,url):
     try:
          title = get_soundcloud_title(url)
          command = f'scdl -l {url} --onlymp3 --name-format {title}'

          result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE)

          audio_data = io.BytesIO(result.stdout)
          audio_data.name = title
          with open(f'{title}.mp3',"rb") as file:
               send_audio(file,title,chat_id,message_id)
               file.close
          os.remove(f"./{title}.mp3")
          return None
     except subprocess.CalledProcessError:
        raise RuntimeError("Fehler beim Download!")
     
def send_audio(audio_data,title,chat_id,message_id):
    files = {'audio': (title,audio_data,'audio/mpeg')}
    data = {'chat_id':chat_id}
    response = requests.post(TELEGRAM_API_URL+"sendAudio", data=data, files=files)
    response = requests.post(TELEGRAM_API_URL+"deleteMessage", {'chat_id': chat_id, 'message_id' : message_id})
    

def get_soundcloud_title(url):
    api_url = f"https://soundcloud.com/oembed?format=json&url={url}"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        primary_title = re.sub(r"[^a-zA-Z.]","",str(data['title']))


        if ".mp3" in primary_title:
            final_title = primary_title.split(".mp3",1)[0]
            return final_title
        else:
            return primary_title
    else:
        return None