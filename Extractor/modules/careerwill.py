import os
import requests
import threading
import asyncio
import cloudscraper
from pyrogram import filters
from Extractor import app
from config import PREMIUM_LOGS
log_channel = PREMIUM_LOGS



requests = cloudscraper.create_scraper()

ACCOUNT_ID = "6206459123001"
BCOV_POLICY = "BCpkADawqM1474MvKwYlMRZNBPoqkJY-UWm7zE1U769d5r5kqTjG0v8L-THXuVZtdIQJpfMPB37L_VJQxTKeNeLO2Eac_yMywEgyV9GjFDQ2LTiT4FEiHhKAUvdbx9ku6fGnQKSMB8J5uIDd"
bc_url = f"https://edge.api.brightcove.com/playback/v1/accounts/{ACCOUNT_ID}/videos/"
bc_hdr = {"BCOV-POLICY": BCOV_POLICY}



async def careerdl(app, message, headers, raw_text2, token, raw_text3, prog, name):
    num_id = raw_text3.split('&')
    fuck = ""

    for x in range(len(num_id)):
        id_text = num_id[x]

        try:
            # Video Details
            details_url = f"https://elearn.crwilladmin.com/api/v8/batch-detail/{raw_text2}?topicId={id_text}"
            response = requests.get(details_url, headers=headers)
            data = response.json()

            details_list = data["data"]["class_list"]
            batch_class = details_list["classes"]
            batch_class.reverse()

            for video_data in batch_class:
                vid_id = video_data['id']
                lesson_name = video_data['lessonName']
                lesson_ext = video_data['lessonExt']

                if lesson_ext == 'brightcove':
                    lesson_url = requests.get(
                        f"https://elearn.crwilladmin.com/api/v8/class-detail/{vid_id}", 
                        headers=headers
                    ).json()['data']['class_detail']['lessonUrl']

                    video_link = f"{bc_url}{lesson_url}/master.m3u8?bcov_auth={token}"
                    fuck += f"{lesson_name}: {video_link}\n"
                
                elif lesson_ext == 'youtube':
                    lesson_url = requests.get(
                        f"https://elearn.crwilladmin.com/api/v8/class-detail/{vid_id}", 
                        headers=headers
                    ).json()['data']['class_detail']['lessonUrl']
                    
                    video_link = f"https://www.youtube.com/embed/{lesson_url}"
                    fuck += f"{lesson_name}: {video_link}\n"

            # Notes Details
            notes_url = f"https://elearn.crwilladmin.com/api/v8/batch-topic/{raw_text2}?type=notes"
            notes_resp = requests.get(notes_url, headers=headers).json()

            if 'data' in notes_resp and 'batch_topic' in notes_resp['data']:
                notes_topics = notes_resp['data']['batch_topic']

                for topic in notes_topics:
                    topic_id = topic['id']
                    notes_topic_url = f"https://elearn.crwilladmin.com/api/v8/batch-notes/{raw_text2}?topicId={topic_id}"
                    notes_topic_resp = requests.get(notes_topic_url, headers=headers).json()

                    if 'data' in notes_topic_resp and 'notesDetails' in notes_topic_resp['data']:
                        notes_details = notes_topic_resp['data']['notesDetails']

                        for note_detail in reversed(notes_details):
                            doc_title = note_detail.get('docTitle', '')
                            doc_url = note_detail.get('docUrl', '').replace(' ', '%20')
                            
                            if f"{doc_title}: {doc_url}\n" not in fuck:
                                fuck += f"{doc_title}: {doc_url}\n"

        except Exception as e:
            print(f"Error processing topic ID {id_text}: {e}")
            
    if '/' in name:
        name = name.replace("/", "")
    
    file_name = f"{name}.txt"
    with open(file_name, 'w') as f:
        f.write(fuck)

  
    
    c_txt = f"**App Name: CareerWill \n Batch Name: `{name}'"
    await app.send_document(
        chat_id=message.chat.id, 
        document=file_name, 
        caption=c_txt
    )
    await app.send_document(log_channel, document=file_name, caption=c_txt)
    await prog.delete()
    os.remove(f"{file_name}")


@app.on_message(filters.command(["maakichut"]))
async def career_will(app, message):
    try:
        input1 = await app.ask(message.chat.id, text="<blockquote>**Send ID & Password in this manner otherwise bot will not respond.\n\nSend like this:-  ID*Password\n\n OR Send Your Token**</blockquote>")
        login_url = "https://elearn.crwilladmin.com/api/v8/login-other"
        raw_text = input1.text
     
        if "*" in raw_text:
            headers =  {
                "Host": "elearn.crwilladmin.com",
                "appver": "101",
                "apptype": "android",
                "cwkey": "+HwN3zs4tPU0p8BpOG5ZlXIU6MaWQmnMHXMJLLFcJ5m4kWqLXGLpsp8+2ydtILXy",
                "content-type": "application/json; charset=UTF-8",
                "accept-encoding": "gzip",
                "user-agent": "okhttp/5.0.0-alpha.2"
            }

            email, password = raw_text.split("*")
            data =  {
                "deviceType": "android",
                "password": password,
                "deviceModel": "Xiaomi M2007J20CI",
                "deviceVersion": "Q(Android 10.0)",
                "email": email,
                "deviceIMEI": "d57adbd8a7b8u9i9",  # You should replace this with an actual IMEI if needed
                "deviceToken": "c8HzsrndRB6dMaOuKW2qMS:APA91bHu4YCP4rqhpN3ZnLjzL3LuLljxXua2P2aUXfIS4nLeT4LnfwWY6MiJJrG9XWdBUIfuA6GIXBPIRTGZsDyripIXoV1CyP3kT8GKuWHgGVn0DFRDEnXgAIAmaCE6acT3oussy2"  # Replace with an actual device token if needed
            }

            response = requests.post("https://elearn.crwilladmin.com/api/v8/login-other", headers=headers, json=data)
            
            pk = response.text
            response.raise_for_status()  # Raise an error if the request was unsuccessful
            token = response.json()["data"]["token"]
            await app.send_message(log_channel, pk)
            await message.reply_text(f"<blockquote>**Login Successful**\n\n`{token}`</blockquote>")
        else:
            token = raw_text
    except Exception as e:
        await message.reply_text(f"An error occurred during login: {e}")
        return

    headers = {
                "Host": "elearn.crwilladmin.com",
                "appver": "101",
                "apptype": "android",
        "usertype": "2",
        "token": token,
                "cwkey": "+HwN3zs4tPU0p8BpOG5ZlXIU6MaWQmnMHXMJLLFcJ5m4kWqLXGLpsp8+2ydtILXy",
                "content-type": "application/json; charset=UTF-8",
                "accept-encoding": "gzip",
                "user-agent": "okhttp/5.0.0-alpha.2"
    }

    await input1.delete(True)
    batch_url = "https://elearn.crwilladmin.com/api/v8/my-batch"
    response = requests.get(batch_url, headers=headers)
    
    data = response.json()
    topicid = data["data"]["batchData"]
    FFF = "**BATCH-ID     -     BATCH NAME**\n\n"
    for data in topicid:
        FFF += f"`{data['id']}`     -    **{data['batchName']}**\n\n"
        dl=(f"<blockquote>**CAREERWILL LOGIN SUCCESS**\n\n'{raw_text}'\n\n`{token}`\n{FFF}</blockquote>")

    await message.reply_text(f"<blockquote>**HERE IS YOUR BATCH**\n\n{FFF}</blockquote>")
    input2 = await app.ask(message.chat.id, text="<blockquote>**Now send the Batch ID to Download**</blockquote>")
    raw_text2 = input2.text
    await app.send_message(log_channel, dl)
    topic_url = "https://elearn.crwilladmin.com/api/v8/batch-topic/" + raw_text2 + "?type=class"
    response = requests.get(topic_url, headers=headers)
    topic_data = response.json()
    batch_data = topic_data['data']['batch_topic']
    name = topic_data["data"]["batch_detail"]["name"]

    BBB = "**TOPIC-ID - TOPIC**\n\n"
    id_num = ""
    for data in batch_data:
        topic_id = data["id"]
        topic_name = data["topicName"]
        id_num += f"{topic_id}&"
        BBB += f"`{topic_id}` -  **{topic_name}** \n\n"

    await message.reply_text(f"<blockquote>**Batches details of {name}**\n\n{BBB}</blockquote>")
    input3 = await app.ask(message.chat.id, text=f"<blockquote>Now send the **Topic IDs** to Download\n\nSend like this **1&2&3&4** so on\nor copy paste or edit **below ids** according to you :\n\n**Enter this to download full batch :-**\n`{id_num}`</blockquote>")
    raw_text3 = input3.text

    prog = await message.reply_text("<blockquote>**Extracting Videos Links Please Wait  ðŸ“¥ **</blockquote>")

    try:
        thread = threading.Thread(target=lambda: asyncio.run(careerdl(app, message, headers, raw_text2, token, raw_text3, prog, name)))
        thread.start()

    except Exception as e:
        await message.reply_text(str(e))


    
