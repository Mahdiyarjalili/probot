import requests
from probot.main import views as main
from probot.main.credentials import TELEGRAM_API_URL, URL,TOKEN
from django.http import HttpResponse
import os
from io import BytesIO
from pdf2image import convert_from_path
from fpdf import FPDF
from PIL import Image
import tempfile

def setwebhook(request):
  response = requests.post(TELEGRAM_API_URL+ "setWebhook?url=" + URL).json()
  return HttpResponse(f"{response}")

FILE_DOWNLOAD_URL = f'https://api.telegram.org/file/bot{TOKEN}'
def pdf_to_image(chat_id, file_id):
    """Lädt das PDF herunter, konvertiert es in Bilder und sendet sie zurück."""
    file_url = f"{TELEGRAM_API_URL}getFile?file_id={file_id}"
    response = requests.get(file_url).json()
    if 'result' in response:
        file_path = response['result']['file_path']
        download_url = f"{FILE_DOWNLOAD_URL}/{file_path}"
        pdf_path = 'temp.pdf'
        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(requests.get(download_url).content)

        main.send_message("sendMessage", {'chat_id': chat_id, 'text': "Converting PDF to images..."})

        try:
            images = convert_from_path(pdf_path, dpi=200)
            for i, image in enumerate(images):
                img_path = f"temp_page_{i+1}.jpg"
                image.save(img_path, "JPEG")
                
                with open(img_path, "rb") as img:
                    requests.post(TELEGRAM_API_URL + "sendPhoto", data={'chat_id': chat_id}, files={"photo": img})

                os.remove(img_path)
        except Exception as e:
            main.send_message("sendMessage", {'chat_id': chat_id, 'text': f"Conversion failed: {e}"})

        #os.remove(pdf_path)
    else:
        main.send_message("sendMessage", {'chat_id': chat_id, 'text': "Failed to get file from Telegram."})

def images_to_pdf(image_list,chat_id):
    pdf = FPDF()
    i = 0
    for img in image_list:
        
        photo_url =f"{TELEGRAM_API_URL}getFile?file_id={img}"
        response = requests.get(photo_url).json()
        photo_path = response['result']['file_path']
        photo_download_url = f'{FILE_DOWNLOAD_URL}/{photo_path}'
        image_content = requests.get(photo_download_url).content
        i +=1
        image_data = BytesIO(image_content)

        image = Image.open(image_data)
        width, height = image.size
        
        img_width_mm = width * 0.264583
        img_height_mm = height * 0.264583
     

        scale_factor = min(pdf.w / img_width_mm, pdf.h / img_height_mm, 1)
        scaled_width = img_width_mm * scale_factor
        scaled_height = img_height_mm * scale_factor

        x_centered = (pdf.w - scaled_width) / 2
        y_centered = (pdf.h - scaled_height) / 2

        with tempfile.NamedTemporaryFile(delete=False,suffix=".jpeg") as temp_file:
            image.save(temp_file, format="JPEG")
            temp_file_path = temp_file.name
    
        pdf.add_page()
       
        pdf.image(temp_file_path,x=x_centered, y=y_centered, w=scaled_width, h=scaled_height)
    pdf.output("output.pdf")  
    with open("output.pdf", "rb") as pdf:
                    requests.post(TELEGRAM_API_URL + "sendDocument", data={'chat_id': chat_id}, files={"document": pdf})
    os.remove("output.pdf")


  