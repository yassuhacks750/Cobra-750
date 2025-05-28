import requests
import json
import random
import uuid
import time
import asyncio
import io
import aiohttp
from pyrogram import Client, filters
import os
import requests
from Extractor import app
from config import PREMIUM_LOGS

log_channel = PREMIUM_LOGS
@app.on_message(filters.command(["adda"]))
async def adda_command_handler(app, m):
    try:
        e_message = await app.ask(m.chat.id, "Send ID & Password of **Adda 247** in given format or just send token.\n\n**Format**:- Email ID*Password")
        ap = e_message.text.strip()
        if "*" in ap:
            e, p = ap.split("*")
        else:
            m.reply_text(" Invalid input. Please send details in the correct format.")
            return
        url = "https://userapi.adda247.com/login?src=aweb"
        data = {"email": e, "providerName": "email", "sec": p}
        headers = {
            "authority": "userapi.adda247.com",
            "Content-Type": "application/json",
            "X-Auth-Token": "fpoa43edty5",
            "X-Jwt-Token": ""
        }

        response = requests.post(url, json=data, headers=headers).json()
        jwt = response.get("jwtToken")
        if not jwt:
            await m.reply_text("Login failed. Please check your credentials.")
            return

        headers["X-Jwt-Token"] = jwt
        packages = requests.get(
            "https://store.adda247.com/api/v2/ppc/package/purchased?pageNumber=0&pageSize=10&src=aweb",
            headers=headers
        ).json().get("data", [])

        for package in packages:
            package_id = package.get("packageId")
            package_title = package.get("title", "").replace('|', '_').replace('/', '_')
            if not package_id or not package_title:
                continue  # Skip if package ID or title is missing

            await m.reply_text(f"Processing package {package_id} ☆ {package_title}")
            start = time.time()
            file_name = f"{package_id}_{package_title}.txt"
            with open(file_name, "w") as file:
                child_packages = requests.get(
                    f"https://store.adda247.com/api/v3/ppc/package/child?packageId={package_id}&category=ONLINE_LIVE_CLASSES&isComingSoon=false&pageNumber=0&pageSize=10&src=aweb",
                    headers=headers
                ).json().get("data", {}).get("packages", [])

                for child in child_packages:
                    child_id = child.get("packageId")
                    child_title = child.get("title", "").replace('|', '_').replace('/', '_')
                    if not child_id or not child_title:
                        continue  # Skip if child ID or title is missing

                    online_classes = requests.get(
                        f"https://store.adda247.com/api/v1/my/purchase/OLC/{child_id}?src=aweb",
                        headers=headers
                    ).json().get("data", {}).get("onlineClasses", [])

                    for online_class in online_classes:
                        class_name = online_class.get("name", "").replace('|', '_').replace('/', '_')
                        if not class_name:
                            continue  # Skip if class name is missing

                        # Handle PDF URL
                        pdf_file = online_class.get("pdfFileName")
                        if pdf_file:
                            pdf_link = f"https://store.adda247.com/{pdf_file}"
                            file.write(f"{class_name}:{pdf_link}\n")

                        # Handle Video URL
                        video_url = online_class.get("url")
                        if video_url:
                            try:
                                video_response = requests.get(
                                    f"https://videotest.adda247.com/file?vp={video_url}&pkgId={child_id}&isOlc=true",
                                    headers=headers
                                ).text
                                for line in video_response.split('\n'):
                                    if "480p30playlist.m3u8" in line:
                                        stream_url = line.replace('/updated', '/demo/updated')
                                        file.write(f"{class_name}:{stream_url}\n")
                            except Exception:
                                continue  # Skip if video URL fails to fetch

            if os.path.getsize(file_name) > 0:
                end = time.time()
                elapsed_time = end-start
                c_text = f"**App Name :** ADDA 247 \n\n BATCH NAME : {package_title}\n\n Elapsed time: {elapsed_time:.1f} seconds \n\n **╾───• JAAT Extractor •───╼**  " 
                await m.reply_document(file_name, caption=c_text)
                await app.send_document(log_channel, file_name , caption = c_text)

    
            os.remove(file_name)

    except requests.exceptions.RequestException as req_err:
        await m.reply_text(f"Request Error: {str(req_err)}")
    except Exception as err:
        await m.reply_text(f"An error occurred: {str(err)}")
