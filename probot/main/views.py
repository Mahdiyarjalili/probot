import json
import requests
import probot.pdf_proccessing.views
from ..main.credentials import TELEGRAM_API_URL, URL
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import requests
from  probot.youtube import views as youtube_views
from probot.pdf_proccessing import views as pdf_views
from probot.soundcloud import views as sc_views

def setwebhook(request):
  response = requests.post(TELEGRAM_API_URL+ "setWebhook?url=" + URL).json()
  return HttpResponse(f"{response}")

@csrf_exempt
def telegram_bot(request):
  if request.method == 'POST':
    update = json.loads(request.body.decode('utf-8'))
    handle_update(update)
    return HttpResponse('ok')
  else:
    return HttpResponseBadRequest('Bad Request')


user_state={}
image_list= []
main_buttons = [
                        [
                            {"text":"PDF Process", "callback_data":"pdf_process"},
                            {"text":"YouTube Downloader","callback_data":"youtube_downloader"}
                        ],
                        [
                            {"text":"SoundCloud Downloader","callback_data":"option_3"},
                        ],
                        [
                            {"text":"E N D", "callback_data":"end"}
                        ]
                    ]
main_discribtion = """<b>Welcome to ProBot</b>

This Telegram bot helps you process various media files! 🎉

🔹 <b>PDF Processing</b>:
    - Convert PDF to Image
    - Convert Images to PDF

🔹 <b>YouTube Downloader</b>: Download videos directly from YouTube.

🔹 <b>SoundCloud Downloader</b>: Download music from SoundCloud to your device.

🔹 More Features: Coming Soon... 🚀

If you ever need help, just reach out. I'm here to assist you. @Mahdiyarjalili
Enjoy!

<b>Created by Mahdiyar</b>
"""
def handle_update(update):
    
    try:
        if 'message' in update:
            chat_id = update['message']['chat']['id']
            message_id = update['message']['message_id']

            if 'text' in update['message']:
                text = update['message']['text']
                if text=="/start":
                     show_menu(chat_id,main_buttons,0 , False, main_discribtion)    
                elif get_user_state(chat_id)=="waiting for receive youtube video url":
                    youtube_views.download_and_send_video(chat_id,text)
                elif get_user_state(chat_id)=="waiting for receive soundcloud audio url":
                    sc_views.download_soundcloud(chat_id,message_id,text)
                elif get_user_state(chat_id) == 'waiting for receive images' and text=='finish':
                    pdf_views.images_to_pdf(image_list,chat_id)
                else:
                     text = update['message']['text']
                     send_message("sendMessage", {
                        'chat_id': chat_id,
                        'text': f'You D said: {text}'
                        })
    

            elif 'document' in update['message']:
                file_id = update['message']['document']['file_id']
                file_name = update['message']['document']['file_name']

                if file_name.endswith(".pdf") and get_user_state(chat_id)=="waiting for receive pdf":
                     probot.pdf_proccessing.views.pdf_to_image(chat_id, file_id)
                else:
                    send_message("sendMessage", {
                        'chat_id': chat_id,
                        'text': "Sorry, I only process PDF files."
                    })
            elif 'photo' in update['message']:
                    photo = update['message']['photo'][-1]
                    photo_id = photo['file_id']
                    if get_user_state(chat_id) == 'waiting for receive images':
                      images(photo_id)

        elif 'callback_query' in update:
                chat_id = update['callback_query']['message']['chat']['id']
                message_id = update['callback_query']['message']['message_id']
                callback_data = update['callback_query']['data']
                if callback_data == 'pdf_process':
                     pdf_process_buttons = [
                        [
                            {"text":"PDF to image", "callback_data":"pdf_to_image"},
                            {"text":"Image to PDF","callback_data":"image_to_pdf"}
                        ],
                        [
                            {"text":"Back","callback_data":"go_back"}
                        ]
                        ]
                     show_menu(chat_id, pdf_process_buttons,message_id, True, "Please choose what do you want do with your Pdf file")
                    
                elif callback_data == 'pdf_to_image':
                    set_user_state(chat_id,"waiting for receive pdf")
                    send_message("sendMessage", {
                        'chat_id': chat_id,
                        'text': "Please send me your pdf file for conversion to image"
                    })
                elif callback_data == 'image_to_pdf':
                    set_user_state(chat_id,"waiting for receive images")
                    image_list.clear()

                    send_message("sendMessage", {
                        'chat_id': chat_id,
                        'text': "Please send me your images for conversion to pdf"
                    })    
                elif callback_data == 'youtube_downloader':
                    set_user_state(chat_id,"waiting for receive youtube video url")
                    send_message("sendMessage", {
                        'chat_id': chat_id,
                        'text': "Please enter a valid YouTube video url"
                    })
                elif callback_data == 'go_back':
                        show_menu(chat_id, main_buttons,message_id,True,main_discribtion)

                elif callback_data == 'end':
                        data={
                            'chat_id':chat_id,
                            'message_id' : message_id
                        }
                        requests.post(TELEGRAM_API_URL+"deleteMessage", data=data)
                else:
                    set_user_state(chat_id,"waiting for receive soundcloud audio url")
                    send_message("sendMessage", {
                        'chat_id': chat_id,
                        'text': "Please enter a valid SoundCloud audio url"
                    })


        else:
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': 'Sorry, I did not understand your message type.'
                })


    except KeyError as e:
        print(f"KeyError: {e} - check if 'message' and expected keys exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

def send_message(method, data):
    return requests.post(TELEGRAM_API_URL + method, data)

def show_menu(chat_id, buttons,message_id, delete, describtion):
    if delete:
        data = {
            'chat_id':chat_id,
            'message_id':message_id
        }
        requests.post(TELEGRAM_API_URL + "deleteMessage", data=data)

    keyboard ={
        "inline_keyboard": buttons
    }
    data ={
        'chat_id': chat_id,
        'text' :describtion,
        'reply_markup': json.dumps(keyboard),
        'parse_mode':'HTML'
    }
    requests.post(TELEGRAM_API_URL + "sendMessage", data=data)

    
def set_user_state(chat_id, state):
    user_state[chat_id] = state

def get_user_state(chat_id):
     return user_state[chat_id]
def images(image_id):
     image_list.append(image_id)
