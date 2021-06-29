import os
import boto3
from PIL import Image
import requests
from telegram.ext import *
import io
import urllib.request
import trp
import json


#key is stored in the OS's environment
key  = os.environ.get('bladerunner_token')
PORT = int(os.environ.get('PORT', 5000))
upd  = Updater(token=key,use_context=True)
dispatcher = upd.dispatcher 
bucketName = "riskybucket69"


new_id = "xyz3"
#universal_chat_id = "hjhjh"


def photo_details(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,text='Photo recieved.Processing')
    universal_chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=universal_chat_id,text='gimme a sec')
    print("Going to get the photo id to send it to textract now")        
    new_id=update.message.photo[-1].file_id
    URL = (context.bot.get_file(new_id)["file_path"])
    IMG_NAME = (URL.split("/",6)[6])
    file_saver(URL,IMG_NAME,update, context,universal_chat_id)

    


def file_saver(url_of_image,file_name,update, context,universal_chat_id):
    response = requests.get(url_of_image)
    image_local = response.content
    uploader(file_name,image_local,update, context,universal_chat_id)
    

def uploader(img_name,local_image,update, context,universal_chat_id):
    s3 = boto3.resource('s3')
    print("pre upload text")
    print()
    s3.Bucket(bucketName).put_object(Key=img_name,Body=local_image)
    print("Image upload successful")
    processor(img_name,update, context,universal_chat_id)

def processor(ultimate,update, context,universal_chat_id):
    textract = boto3.client('textract')
    print("almost printing text")
    response = textract.detect_document_text(
        Document = {
            'S3Object':{
                'Bucket':bucketName,
                'Name':ultimate
            }
        }
        
    )
    print("printing the final text")
    lines = [item["Text"] for item in response["Blocks"] if item["BlockType"] == "LINE"]    
    final_f = " ".join(lines)
    #printer(final_f)
    printer(update, context,final_f,universal_chat_id) 

def printer(update,context,final_f,universal_chat_id):
    context.bot.send_message(chat_id=universal_chat_id,text=final_f)

#def send_reply(reply):
    #context.bot.send_message(chat_id = universal_chat_id,text = reply)



recieve_handler = MessageHandler(Filters.photo,photo_details)
dispatcher.add_handler(recieve_handler)



#starts "monitoring" the bot chat box for events
#upd.start_polling()


#webhooks?
upd.start_webhook(listen="0.0.0.0",
                  port=int(PORT),
                  url_path=key)
upd.bot.setWebhook('https://officerk-bot.herokuapp.com/' + key)



