import json
import random
import string
import names
import config
from art import text2art
import names
import random
import datetime
import platform
import os
import base64
import requests
import re
import httpagentparser
import time
import sys
import ctypes
from multiprocessing import RawValue, Lock
import names
from PIL import Image, ImageDraw, ImageFilter
import threading

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

def get_build_number():
    try:
        asset_res = requests.get("https://discord.com/app", allow_redirects=False, headers= { "user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"})
        for asset in reversed(re.compile(r'([a-zA-z0-9]+).js').findall(asset_res.text)):
            if has_numbers(asset):
                asset_string = asset
                break
        build_res = requests.get(f"https://discord.com/assets/{asset_string}.js", headers= { "user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"})
        return build_res.text.split('Build Number: ").concat("')[1].split('"')[0]
    except:
        return 210099

BUILD_NUMBER = get_build_number()

def print_title() -> None:
    '''
    Takes script name from static_values.py and convert to ascii art
    Splits the name so each word is on a different line
    '''
    split_name = config.script_name.split(" ")
    for word in split_name:
        print(text2art(word))

def load_all_proxies() -> list[dict]:
    """
    Load a list of proxies from a text file and format them for use with the 'requests' library.

    :return: A list of dictionaries containing formatted proxies.
    """
    with open('proxies.txt') as f:
        proxy_file = f.read().splitlines()
    all_proxies = []
    for proxy in proxy_file:
        try:
            split_proxy = proxy.split(":")
            proxy_dict = {
                "http": f"http://{split_proxy[2]}:{split_proxy[3]}@{split_proxy[0]}:{split_proxy[1]}",
                "https": f"http://{split_proxy[2]}:{split_proxy[3]}@{split_proxy[0]}:{split_proxy[1]}"
            }
            all_proxies.append(proxy_dict)
        except:
            proxy_dict = {
                "http": "http://"+proxy,
                "https": "http://"+proxy
            } 
            all_proxies.append(proxy_dict)
    return all_proxies


def catchAll_gen(domain):
    name = names.get_full_name().replace(" ", "")
    return f"{name}{random.randint(1000,9999)}@{domain}"

def generate_dob(age):
    current_date = datetime.date.today()
    birth_year = current_date.year - age
    birth_month = random.randint(1, 12)
    max_day = (current_date.replace(year=birth_year, month=birth_month, day=1) - datetime.timedelta(days=1)).day
    birth_day = random.randint(1, max_day)
    dob = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"

    return dob

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    print_title()

def get_bifrost_path(folder_name) -> str:
    '''
    params: name of folder containing bifrost file : string

    returns path to the file depending on if file system is windows or linux

    :return: bifrost_path : string
    '''
    os_name = platform.system()

    if os_name == "Linux":
        bifrost_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), folder_name, "bifrost-0.1.8-linux.x86_64.so")
    elif os_name == "Windows":
        bifrost_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), folder_name, "bifrost-0.1.8-windows.x86_64.dll")

    return bifrost_path

import random
import string

def random_string(length):
    letters = string.ascii_letters + string.digits
    b = [random.choice(letters) for _ in range(length)]
    return ''.join(b)
    
def load_random_username():
    if config.real_usernames:
        with open("data/usernames.txt", "r", encoding="UTF-8") as f:
            return random.choice(f.read().splitlines())
    else:
        return f"{names.get_first_name()}{random.randint(5, 10)}"

def GenerateBornDate():
    year=str(random.randint(1997,2001));month=str(random.randint(1,12));day=str(random.randint(1,28))
    if len(month)==1:month='0'+month
    if len(day)==1:day='0'+day
    return year+'-'+month+'-'+day

def load_tokens():
    with open('output/tokens.txt', 'r') as token_file:
        token_arr = token_file.read().splitlines()
        print(f"Total tokens : {len(token_arr)}")
        return token_arr
    
def get_os_name(os: str):
    if os.lower() == "macintosh":
        return "Mac OS X"
    else:
        return os
    
def get_trackers(useragent, encoded = True):
    res = httpagentparser.detect(useragent)
    browser = res["browser"]["name"]
    if "chro" in browser.lower():
        browser = "Chrome"
    properties = {
        "os": get_os_name(res["os"]["name"]),
        "browser": browser,
        "device":"",
        "system_locale":"en-US",
        "browser_user_agent":useragent,
        "browser_version":res["browser"]["version"],
        "os_version":res["platform"]["version"].replace("X", '').strip(),
        "referrer":"https://discord.com/",
        "referring_domain":"discord.com",
        "referrer_current":"https://discord.com/",
        "referring_domain_current":"discord.com",
        "release_channel":"stable",
        "client_build_number":int(BUILD_NUMBER),
        "client_event_source":None
    }
    
    return base64.b64encode(json.dumps(properties, separators=(',', ':')).encode()).decode() if encoded else properties

def get_identifier(useragent: str) -> str:
    browser_obj = httpagentparser.detect(useragent)
    name: str = browser_obj["browser"]["name"]
    version: str = browser_obj["browser"]["version"]
    if name.lower() == "chrome":
        chrome_version = version.split(".", 1)[0]
        if int(chrome_version) <= 108:
            return f"chrome_{chrome_version}"
        else:
            return f"chrome{chrome_version}"
    elif name.lower() == "safari":
        safari_version = version.replace(".", "_")
        return f"safari_{safari_version}"
    elif name.lower() == "firefox":
        ff_version = version.split(".", 1)[0]
        if int(ff_version) <= 104:
            return f"firefox_{ff_version}"
        else:
            return f"firefox{ff_version}"
    elif name.lower() == "opera":
        opera_version = version.split(".", 1)[0]
        return f"opera_{opera_version}"
    else:
        return "chrome114"
    
def test_properties(target_json):
    useragents = []
    with open(target_json, "r", encoding="UTF-8") as f:
        ua_obj = json.load(f)
        for ua in ua_obj:
            try:
                get_trackers(ua["useragent"])
                useragents.append(ua["useragent"])
            except Exception as e:
                pass
    
    os.remove(target_json)
        
    with open("user_agents.json", "w", encoding="UTF-8") as file:
        file.write(json.dumps(useragents))
        
class Counter(object):
    '''
    Counter class that extends object type
    params: initial value (0 by default)

    provides 2 methods:
        increment() to increment the shared value by 1
        value() to read the value in a thread safe way
            :return: value: int
    '''
    def __init__(self, value=0):
        self.val = RawValue('i', value)
        self.lock = Lock()

    def increment(self):
        with self.lock:
            self.val.value += 1

    def value(self):
        with self.lock:
            return self.val.value
        
def update_title(token_counter: Counter):
    platform = sys.platform
    while token_counter.value() == 0:
        pass
    else:
        st = time.time()
        while True:
            time.sleep(1.0 - ((time.time() - st) % 1.0))
            tpm = round(token_counter.value()/((st - time.time())/60), 2)
            title_string = f"Tokens genned : {token_counter.value()} | RPM : {tpm}"
            if platform == "darwin":
                print("MacOs")
                cmd = "\033]0;{}\007".format(title_string)
                sys.stdout.write(cmd)
            elif platform == "win32" or platform == "cygwin":
                ctypes.windll.kernel32.SetConsoleTitleW(title_string)
            else:
                pass
            
def generate_discord_bio():
    templates = [
        "Just a {adjective} soul exploring the digital realms.",
        "Part-time {occupation}, full-time {adjective} enthusiast.",
        "Finding joy in pixels and words. Virtual adventures await!",
        "Living life one server at a time.",
        "Professional meme connoisseur, spreading laughter across the internet.",
        "Passionate {hobby} lover. Hit me up to connect!",
        "World traveler ✈️ Virtual explorer 🖱️",
        "Forever dreaming in code, and making magic happen online.",
        "Obsessed with cats 🐱 and virtual communities. Join me!",
        "Just a {adjective} individual with a penchant for {hobby}.",
        "Always up for a good conversation. Let's connect!",
        "Emoji lover 😄 and enthusiast. Let's chat!",
        "Exploring the endless possibilities of the digital realm. Join me on this journey!",
        "Constantly tinkering with bots and scripts. Let's build something together!",
        "Finding solace in virtual embrace. Join my community for good vibes!",
        "Avid {hobby} practitioner and aficionado. Hit me up!",
        "Spreading positivity and laughter. Join my community for a good time!",
        "Adventurous soul navigating the vast landscapes of virtual communities. Care to join?",
        "Forever grateful for the friendships I've found online. Let's connect!",
        "Seeking inspiration and creative minds. Join my community!",
        "Embracing the wonders of the digital world. Let's explore together!",
        "Exploring the digital universe one {adjective} step at a time.",
        "Part-time {occupation}, full-time digital adventurer.",
        "Unleashing creativity in the virtual realm.",
        "Living life one pixel at a time.",
        "Spreading laughter and positivity across the web.",
        "Finding solace in {adjective} virtual communities.",
        "Passionate {hobby} lover. Let's connect and share the passion!",
        "Traveling through cyberspace, discovering new horizons.",
        "Making magic happen in the digital realm.",
        "Cats and {adjective} vibes rule my virtual world. Join me!",
        "Just a {adjective} soul with a knack for {hobby}.",
        "Seeking engaging conversations and meaningful connections.",
        "Emoji enthusiast 😄 Let's express ourselves virtually!",
        "Embarking on a virtual journey of endless possibilities.",
        "Tinkering with bots and scripts, building the future together!",
        "Creating a virtual haven of good vibes. Join my community!",
        "Mastering the art of {hobby} in the digital realm. Join me!",
        "Bringing joy and laughter to the digital landscape. Join my community!",
        "Exploring the vast frontiers of virtual communities. Join the adventure!",
        "Grateful for the online friendships that enrich my life. Let's connect!",
        "Seeking inspiration and creative minds to collaborate with. Join my community!",
    ]
    
    adjectives = ["creative", "curious", "enthusiastic", "friendly", "geeky", "adventurous", "passionate", "imaginative", "whimsical", "innovative"]
    occupations = ["developer", "designer", "musician", "writer", "gamer", "artist", "student", "photographer", "chef", "explorer"]
    hobbies = ["photography", "cooking", "reading", "gaming", "gardening", "playing an instrument", "hiking", "painting", "writing", "yoga"]
    
    template = random.choice(templates)
    
    bio = template.format(
        adjective=random.choice(adjectives),
        occupation=random.choice(occupations),
        hobby=random.choice(hobbies)
    )
    
    return bio

def load_useragents(path = "data/user_agents.json"):
    with open(path, "r", encoding="UTF-8") as f:
        return json.load(f)

def resize_image():
    print("Running formatted...")
    for image in os.listdir("data/unformatted_pfps"):
        try:
            img = Image.open(f"data/unformatted_pfps/{image}")
            img.thumbnail((128,128))
            img.save(f"data/formatted_pfps/pfp_{random_string(5)}.jpg")
        except:
            pass
        
def get_random_pfp():
    pfp_path = random.choice(os.listdir("data/formatted_pfps"))
    with open(f"data/formatted_pfps/{pfp_path}", 'rb') as f:
        b64_str = base64.b64encode(f.read()).decode('utf-8')
        ext = pfp_path.split('.')[-1]
        return f'data:image/{ext};base64,{b64_str}'
    
def getWebsocketData(token, super_props):
    return {
        "op":2,
        "d":{
            "token":token,
            "capabilities":125,
            "properties": decode_super_props(super_props),
            "presence":{
                "status":"unknown",
                "since":0,
                "activities":[
                    
                ],
                "afk": bool(random.getrandbits(1))
            },
            "compress":False,
            "client_state":{
                "guild_versions":{
                    
                },
                "highest_last_message_id":"0",
                "read_state_version":0,
                "user_guild_settings_version":-1,
                "user_settings_version":-1,
                "private_channels_version":"0",
                "api_code_version":0
            }
        }
}
    
def get_random_properties():
    with open("data/session_properties.json", "r+", encoding="UTF-8") as f:
        return random.choice(json.load(f))
    
def decode_super_props(prop_string: str):
    props_dict = json.loads(base64.b64decode(prop_string))
    props_dict["client_build_number"] = BUILD_NUMBER
    return props_dict

def get_session_props():
    with open("data/session_properties.json", "r", encoding="UTF-8") as f:
        dict = json.loads(f.read())
        props = random.choice(dict)
        return props["x-super-properties"], props["useragent"], props["ja3"]
    
def getWebsocketData_v1(token, useragent):
    game = "Monsoon"
    return {
   "op":2,
   "d":{
      "token":token,
      "capabilities":8189,
      "properties":{
         "os":"Windows",
         "browser":"Chrome",
         "device":"",
         "system_locale":"en-US",
         "browser_user_agent":useragent,
         "browser_version":"114.0.0.0",
         "os_version":"10",
         "referrer":"https://www.google.com/",
         "referring_domain":"www.google.com",
         "search_engine":"google",
         "referrer_current":"",
         "referring_domain_current":"",
         "release_channel":"stable",
         "client_build_number":BUILD_NUMBER,
         "client_event_source":None
      },
      "presence":{
         "status":"unknown",
         "since":0,
         "activities":[
            
         ],
         "afk":False
      },
      "compress":False,
      "client_state":{
         "guild_versions":{
            
         },
         "highest_last_message_id":"0",
         "read_state_version":0,
         "user_guild_settings_version":-1,
         "user_settings_version":-1,
         "private_channels_version":"0",
         "api_code_version":0
      }
   }
}
    
write_lock = threading.Lock()

def write_success(token, type):
    if type == "verified":
        path = "output/verified_tokens.txt"
    elif type == "unverified":
        path = "output/unverified_tokens.txt"
    else:
        print("Invalid token type...")
        return
    with open(path, "w", encoding="UTF-8") as f:
        f.write(token + "\n")
    
