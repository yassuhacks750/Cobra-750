import requests 
import datetime, pytz, re, aiofiles, subprocess, os, base64, io
import aiohttp
import aiofiles
import os
import server 
from pyrogram import Client
from pyrogram import filters
from Extractor import app
from config import PREMIUM_LOGS

log_channel = PREMIUM_LOGS
async def fetchs(url, json=None, headers=None):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json, headers=headers) as response:
            return await response.json()

async def login(app, m, all_urls, start_time, bname, batch_id, app_name, price=None, start_date=None, imageUrl=None):
    bname = await sanitize_bname(bname)
    file_path = f"{bname}.txt"
    local_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
    end_time = datetime.datetime.now()
    duration = end_time - start_time
    minutes, seconds = divmod(duration.total_seconds(), 60)
    all_text = "\n".join(all_urls)
    video_count = len(re.findall(r'\.(m3u8|mpd|mp4)', all_text))
    pdf_count = len(re.findall(r'\.pdf', all_text))
    drm_video_count = len(re.findall(r'\.(videoid|mpd|testbook)', all_text))
    enc_pdf_count = len(re.findall(r'\.pdf\*', all_text))
    caption = (f"**APP NAME :** STUDY IQ\n\n **ID - Batch Name:** {batch_id} - {bname} \n\n TOTAL LINK - {len(all_urls)} \n Video Links - {video_count - drm_video_count} \n Total Pdf - {pdf_count} \n\n  **╾───• Cobra Extractor •───╼** ")
    async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
        await f.writelines([url + '\n' for url in all_urls])
    copy = await m.reply_document(document=file_path,caption=caption)
    await app.send_document(log_channel, file_path, caption=caption)
    
async def sanitize_bname(bname, max_length=50):
    bname = re.sub(r'[\\/:*?"<>|\t\n\r]+', '', bname).strip()
    if len(bname) > max_length:
        bname = bname[:max_length]
    return bname

@app.on_message(filters.command(["iq"]))
async def handle_iq_logic(app, m):
    editable = await m.reply_text("**Now Send your phone number without country code or Token**")
    input1: Message = await app.listen(chat_id=m.chat.id)
    await input1.delete()
    raw_text1 = input1.text.strip()
    logged_in = False

    if raw_text1.isdigit():
        phNum = raw_text1.strip()
        master0 = await fetchs(f"https://www.studyiq.net/api/web/userlogin", json={"mobile": phNum})
        msg = master0.get('msg')
        if master0['data']:
            user_id = master0.get('data', {}).get('user_id')
            await editable.edit(f"**Massage:**{msg}")
        else:
            await editable.edit(f"**Massage:**{msg}")
    
        input2 = await app.listen(chat_id=m.chat.id)
        raw_text2 = input2.text.strip()
        otp = raw_text2
        await input2.delete()
        data = {
            "user_id": user_id,
            "otp": otp
        }

        master1 = await fetchs(f"https://www.studyiq.net/api/web/web_user_login", json=data)
        msg = master1.get('msg')
        if master1['data']:  
            token = master1.get('data', {}).get('api_token')
            if token:
                await m.reply_text(f"**Massage :-** {msg}\n\n**Your Access Token for future uses:** `{token}`")
                logged_in = True
            else:
                await editable.edit(f"**Massage:**{msg}")     
    else:
        token = raw_text1.strip()
        logged_in = True

    if logged_in:
        headers = {
            "Authorization": f"Bearer {token}",
        }
        json_master2 = server.get("https://backend.studyiq.net/app-content-ws/api/v1/getAllPurchasedCourses?source=WEB", headers=headers)
        if not json_master2['data']:
            await editable.edit("You don't have any Paid & free batches available.")
            return

        Batch_ids = []
        cool = ""
        FFF = "**BATCH-ID  -  BATCH NAME**"

        for course in json_master2["data"]:
            raz = f"`{course['courseId']}` - **{course['courseTitle']}**\n\n"
            if len(f'{cool}{raz}') > 4096:
                cool = ""
            cool += raz
            Batch_ids.append(course["courseId"])

        Batch_ids_str = '&'.join(map(str, Batch_ids))
        print(Batch_ids_str)
        await editable.edit(f'{"**You have these batches :-**"}\n\n{FFF}\n\n{cool}')
        editable1 = await m.reply_text(f"**Now send the Batch ID to Download**\n\n**For All batch -** `{Batch_ids_str}`")
        
        input4 = await app.listen(chat_id=m.chat.id)
        await input4.delete()
        await editable.delete()
        await editable1.delete()

        if "&" in input4.text:
            batch_ids = input4.text.split('&')
        else:
            batch_ids = [input4.text]

        for batch_id in batch_ids:
            start_time = datetime.datetime.now()
            edit_t = await m.reply_text("**Please wait url scrapping start**")

            if batch_id:
                master3 = server.get(f"https://backend.studyiq.net/app-content-ws/v1/course/getDetails?courseId={batch_id}&languageId=", headers=headers)
                bname = master3.get("courseTitle").replace(' || ', '').replace('|', '') 
                all_urls = []
                T_slug = "&".join([str(item.get("contentId")) for item in master3['data']])
                content_id = T_slug.split('&')

                for t_id in content_id:
                    topicname = next((x.get('name') for x in master3['data'] if x.get('contentId') == int(t_id)), None)
                    try:
                        await edit_t.edit(f"(ðŸ‘‰ï¾Ÿãƒ®ï¾Ÿ)ðŸ‘‰**Url writing in process -** `{topicname}`")
                    except Exception as e:
                        print(f"Error occurred while editing topic name: {e}")

                    parent_data = server.get(f"https://backend.studyiq.net/app-content-ws/v1/course/getDetails?courseId={batch_id}&languageId=&parentId={t_id}", headers=headers)
                    subFolderOrderId = [item.get("subFolderOrderId") for item in parent_data['data']]

                    if all(sub_folder_order_id is None for sub_folder_order_id in subFolderOrderId):
                        for video_item in video['data']:
                            url = video_item.get('videoUrl')
                            name = video_item.get('name')
                            if url is not None:
                                if url.endswith(".mpd"):
                                    cc = f"[{topicname}]-{name}:{url}"
                                else:
                                    cc = f"[{topicname}]-{name}:{url}"
                                
                                all_urls.append(cc)
                            contentIdy = video_item.get('contentId')
                            response = await fetchs(f"https://backend.studyiq.net/app-content-ws/api/lesson/data?lesson_id={contentIdy}&courseId={batch_id}", headers=headers)
                            for option in response['options']:
                                if option.get('urls'):
                                    for url_data in option['urls']:
                                        if 'name' in url_data:
                                            name = url_data['name']
                                            url = url_data['url']
                                            cc = f"[Notes] - {name}: {url}"
                                            
                                            all_urls.append(cc)

                    else:
                        T_slug = "&".join([str(item.get("contentId")) for item in parent_data['data']])
                        content_idx = T_slug.split('&')

                        for p_id in content_idx:
                            course_title = next((x.get('name') for x in parent_data['data'] if x.get('contentId') == int(p_id)), None)
                            video = server.get(f"https://backend.studyiq.net/app-content-ws/v1/course/getDetails?courseId={batch_id}&languageId=&parentId={t_id}/{p_id}", headers=headers)
                            for video_item in video['data']:
                                url = video_item.get('videoUrl')
                                name = video_item.get('name')
                                if url is not None:
                                    if url.endswith(".mpd"):
                                        cc = f"[{course_title}]-{name}:{url}"
                                    else:
                                        cc = f"[{course_title}]-{name}:{url}"
                                    
                                    all_urls.append(cc)
                                contentIdx = video_item.get('contentId')
                                response = await fetchs(f"https://backend.studyiq.net/app-content-ws/api/lesson/data?lesson_id={contentIdx}&courseId={batch_id}", headers=headers)
                                for option in response['options']:
                                    if option.get('urls'):
                                        for url_data in option['urls']:
                                            if 'name' in url_data:
                                                name = url_data['name']
                                                url = url_data['url']
                                                cc = f"[Notes] - {name}: {url}"    
                                                all_urls.append(cc)
                await edit_t.edit('**URL Writing Successfull**')
                await edit_t.delete()
                if all_urls:
                    await login(app, m, all_urls, start_time, bname, batch_id, app_name="Study IQ", price=None, start_date=None, imageUrl=None ,)
                else:
                    await edit_t.edit("**No URLs found**")


    
