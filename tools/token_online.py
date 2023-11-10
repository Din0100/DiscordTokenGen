import websocket
import json
import time
import threading
import ssl
import zlib
import random
import os
import sys

game_list = path = os.path.abspath('./data/game_list.json')

def load_games_list():
    with open("data/game_list.json", "r", encoding="UTF-8") as f:
        return json.load(f)

class DiscordOnlineWebsocket():
    def __init__(self, token: str, useragents, proxies, period = 180) -> None:
        self.token = token
        self.running = True
        self.ua = random.choice(useragents)
        self.period = period
        self.type = random.choice(['Playing', 'Streaming', 'Watching', 'Listening', ''])
        self.status = random.choice(['online', 'dnd', 'idle'])
        try:
            self.proxy = proxies["http"].replace("http://", "")
        except:
            pass
        self.ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.ssl_context.server_hostname = "gateway.discord.gg"
        self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        self.ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
        
        self.ws = websocket.WebSocket()
        
    def send_payload(self, payload: dict) -> None:
        self.ws.send(json.dumps(payload))

    def recieve(self) -> dict:
        data = self.ws.recv()
        if data:
            parsed_res = zlib.decompressobj().decompress(data)
            return json.loads(parsed_res)
        
    def heartbeat(self, interval: float):
        while self.running:
            time.sleep(interval)
            self.send_payload({
                'op': 1,
                'd': None
            })

    def login(self):
        headers = {
            "Origin": "https://discord.com",
		    "User-Agent" : self.ua
        }

        try:
            split1 = self.proxy.split("@")
            auth_split = split1[0].split(":")
            ip_split = split1[1].split(":")
            
            proxy_auth = (auth_split[0], auth_split[1])
            proxy_host = ip_split[0]
            proxy_port = ip_split[1]
        except:
            proxy_auth = None
            proxy_host = None
            proxy_port = None
        
        self.ws.connect('wss://gateway.discord.gg/?encoding=json', headers= headers, host = "gateway.discord.gg", cookies = self.cookies, http_proxy_host=proxy_host, http_proxy_port=proxy_port, proxy_type="http", http_proxy_auth = proxy_auth)
       
        interval = self.recieve()['d']['heartbeat_interval'] / 1000
        threading.Thread(target=self.heartbeat,daemon=True, args=(interval,)).start()
        
    def online(self):
        payload = self.gen_random_payload()
        self.send_payload(payload)
    
    def gen_random_payload(self):
        if self.type == "Playing":
            game = random.choice(game_list)
            gamejson = {
                "name": game,
                "type": 0
            }
        elif self.type == 'Streaming':
            gamejson = {
                "name": game,
                "type": 1,
                "url": ""
            }
        elif self.type == "Listening":
            game = random.choice(["Spotify", "Deezer", "Apple Music", "YouTube", "SoundCloud", "Pandora", "Tidal", "Amazon Music", "Google Play Music", "Apple Podcasts", "iTunes", "Beatport"])
            gamejson = {
                "name": game,
                "type": 2
            }
        elif self.type == "Watching":
            game = random.choice(["YouTube", "Twitch"])
            gamejson = {
                "name": game,
                "type": 3
            }
        else:
            gamejson = {
                "name": game,
                "type": 0
            }
            
        return {
            "op": 2,
            "d": {
                "token": self.token,
                "properties": {
                    "$os": sys.platform,
                    "$browser": "RTB",
                    "$device": f"{sys.platform} Device"
                },
                "presence": {
                    "game": gamejson,
                    "status": self.status,
                    "since": 0,
                    "afk": False
                }
            },
            "s": None,
            "t": None
        }
        
    def run(self):
        self.login()
        self.online()
        print(f"[+] Token : {self.token} is online!")
        if self.period != 0:
            time.sleep(self.period)
            print(f"[+] Token : {self.token} is now offline after {self.period}s")
            self.running = False
        else:
            while True:
                pass
        