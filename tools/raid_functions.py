import sys
import random
import config
import asyncio
import aiohttp
import utils
import random
import random
# from simple_term_menu import TerminalMenu

def get_reason(index):
    reason_options = [
        'Illegal content',
        'Harassment',
        'Spam or phishing links',
        'Self-harm',
        'NSFW content'
    ]
    
    # reason_menu = TerminalMenu(reason_options)
    # reason = reason_menu.show()
    for index, option in enumerate(reason_options):
        print(f"{index} - {option}")
    reason= input()
        
    return reason

user_agents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",]

sem = asyncio.Semaphore(1000)

async def channel_spam_fetch(token, proxies, channel_id, msg):
    async with sem:
        return await mass_channel_spam(token, channel_id, msg, proxies)
    
async def react_spam_fetch(token, proxies, channel_id, msg_id):
    async with sem:
        return await mass_react(token, channel_id, msg_id, proxies)
    
async def report_spam_fetch(token, guild_id, channel_id, message_id, proxies, reason):
    async with sem:
        return await mass_report(token, guild_id, channel_id, message_id, proxies, reason)

async def run(batch, proxies, option):
    tasks = []
    if option == "Channel Spam":
        channel_id = input('Enter the channel ID to spam: ')
        msg = input('Type the message to spam: ')
        for token in batch:
            tasks.append(asyncio.ensure_future(channel_spam_fetch(token, proxies, channel_id, msg)))
    elif option == "Mass React":
        channel_id = input('Enter the channel ID to react in: ')
        msg_id = input('Enter the message ID to react to: ')
        for token in batch:
            tasks.append(asyncio.ensure_future(react_spam_fetch(token, proxies, channel_id, msg_id)))
    elif option == "Mass Report":
        channel_id = input('Enter the channel ID to react in: ')
        msg_id = input('Enter the message ID to react to: ')
        guild_id = input('Enter the guild ID')
        reason = get_reason()
        for token in batch:
            tasks.append(asyncio.ensure_future(report_spam_fetch(token, guild_id, channel_id, msg_id,reason)))
    else:
        print("Invalid Option, exiting script...")
        sys.exit()

def async_task_handler(option, tokens):
    proxies = utils.load_all_proxies()
    split_list = [tokens[x:x+config.batch_size] for x in range(0, len(tokens), config.batch_size)]
    for batch in split_list:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(run(batch, proxies, option))
        

async def mass_channel_spam(token, channel_id, msg, proxies = None):
    connector = aiohttp.TCPConnector(force_close=True, verify_ssl=False, limit=0)
    async with aiohttp.ClientSession(connector=connector, trust_env=True, timeout=aiohttp.ClientTimeout(total=20)) as session:
        headers = {
            'Accept': '*/*',
            "authorization": f"{token}",
            'Content-Type': 'application/json',
            "user-agent" : random.choice(user_agents)
        }
        form_data = {
            "content": msg,
            "nonce": None,
            "tts": False,
            "flags": 0
        }
        proxy = None if proxies is None else random.choice(proxies)
        async with session.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', json=form_data, headers=headers, proxies=proxy) as req:
            if config.logging:
                if str(req.status)[0] == "4":
                    print(f"[⚠] | {token} failed to send message")
                elif req.status in (200, 204):
                    print(f"[✓] | {token} succesfully sent message")
                else:
                    print(f"[?] | Unknown response {req.status} - one of the inputs may be incorrect")

async def mass_react(token, channel_id, msg_id, proxies = None):
    connector = aiohttp.TCPConnector(force_close=True, verify_ssl=False, limit=0)
    async with aiohttp.ClientSession(connector=connector, trust_env=True, timeout=aiohttp.ClientTimeout(total=20)) as session:
        headers = {
            'Accept': '*/*',
            "authorization": f"{token}",
            'Content-Type': 'application/json',
            "user-agent" : random.choice(user_agents)
        }
        proxy = None if proxies is None else random.choice(proxies)
        async with session.put(f"https://discord.com/api/v9/channels/{channel_id}/messages/{msg_id}/reactions/%F0%9F%92%AF/%40me?location=Message&type=0", headers=headers, proxies = proxy) as req:
            if config.logging:
                if str(req.status)[0] == "4":
                    print(f"[⚠] | {token} failed to react")
                elif req.status in (200, 204):
                    print(f"[✓] | {token} succesfully sent message")
                else:
                    print(f"[?] | Unknown response {req.status} - one of the inputs may be incorrect")
                    
async def mass_report(token, guild_id, channel_id, message_id,reason, proxies = None):
    connector = aiohttp.TCPConnector(force_close=True, verify_ssl=False, limit=0)
    async with aiohttp.ClientSession(connector=connector, trust_env=True, timeout=aiohttp.ClientTimeout(total=20)) as session:
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US',
            "user-agent" : random.choice(user_agents),
            'Content-Type': 'application/json',
            'Authorization': token
        }
        
        payload = {
            'channel_id': channel_id,
            'message_id': message_id,
            'guild_id': guild_id,
            'reason': reason
        }
        proxy = None if proxies is None else random.choice(proxies)
        async with session.post("https://discordapp.com/api/v9/report", headers=headers, json = payload, proxies = proxy) as req:
            if req.status == 201:
                print((f"[✓] | {token} has succesfully reported"))
            if req.status in (401, 403):
                print((f"[✓] | {token} has failed to report"))
            else:
                print(f"[?] | Unknown response {req.status} - one of the inputs may be incorrect")