import aiohttp, cloudscraper, requests, re, asyncio, random
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor()
scraper = cloudscraper.create_scraper()

async def fetch_aio(url, headers=None, params=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            return await response.json()

async def post_aio(url, headers=None, json=None):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json) as response:
            return await response.json()
        
def get(url, params=None, headers=None):
    response = scraper.get(url, params=params, headers=headers)
    return response.json()

def post(url, headers=None, data=None):
    response = scraper.post(url, headers=headers, data=data)
    return response.json()

def post_json_body(url, headers=None, json=None):
    response = scraper.post(url, headers=headers, json=json)
    return response.json()

async def sanitize_bname(bname, max_length=50):
    bname = re.sub(r'[\\/:*?"<>|\t\n\r]+', '', bname).strip()
    if len(bname) > max_length:
        bname = bname[:max_length]
    return bname

def direct_get(url):
    response = requests.get(url)
    return response.text

def direct_get_json(url):
    response = scraper.get(url)
    return response.json()


used_tokens = []
async def get_random_token():
    global used_tokens
    if len(used_tokens) == len(appx_token.APPX):
        used_tokens = []  # Reset after using all tokens
    available_tokens = list(set(appx_token.APPX) - set(used_tokens))
    token = random.choice(available_tokens)
    used_tokens.append(token)
    return token

async def fetch_url(url, params=None, headers=None):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, lambda: scraper.get(url, params=params, headers=headers))


async def get_appx(url, params=None, headers=None, retries=10):
    attempt = 0
    while attempt < retries:
        try:
            response = await fetch_url(url, params, headers)
            if response.status_code == 200:
                await asyncio.sleep(0.5)
                return response.json()
            else:
                attempt += 1
                if attempt < retries:
                    LOGGER.error(f"Request failed with status code {response.status_code}. Retrying in 2 minutes 30 seconds... (Attempt {attempt}/{retries})")
                    await asyncio.sleep(20)  # 2 minutes 30 seconds
                else:
                    LOGGER.error("Max retries reached. Unable to fetch data.")
                    raise Exception("Max retries reached")
        except Exception as e:
            attempt += 1
            if attempt < retries:
                LOGGER.error(f"Error occurred: {e}. Retrying in 2 minutes 30 seconds... (Attempt {attempt}/{retries})")
                await asyncio.sleep(20)  # 2 minutes 30 seconds
            else:
                LOGGER.error("Max retries reached. Unable to fetch data.")
                raise

                               
