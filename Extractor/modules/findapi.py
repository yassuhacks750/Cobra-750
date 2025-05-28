from pyrogram import filters
import json
from Extractor import app


@app.on_message(filters.command(["getapi"]))
async def findapis_extract(app, m):
    input = await app.send_message(m.chat.id, "<blockquote>Enter App Name</blockquote>")
    input1 = await  app.listen(input.chat.id)
    try:
        file_path = 'appxapis.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        input2 = ((input1.text.replace(" ", ""))).lower()
        
        search_term = input2        
        if not search_term:
            await m.reply("Please provide a search term. <b>Example:  mahatma</b>")
            return
        
        result = find_api(search_term, data)
        await m.reply(result)
    except Exception as e:
        await m.reply(f"Error: {str(e)}")

def find_api(keyword, data):
    matching_results = [
        f"<b>{item['name']}</b>\n<code>{item['api']}</code>\n\n"
        for idx, item in enumerate(data) 
        if keyword.lower() in item['name'].lower()
    ]
    
    if matching_results:
        return f"Found <b>{len(matching_results)} result(s)</b> for your search term '{keyword}':\n\n" + "\n".join(matching_results)
    else:
        return f"No result found for your search term '{keyword}'"
        
