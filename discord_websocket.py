import websocket
import json
import time
import threading
import ssl
import zlib
import random
import utils

class DiscordWs():
    def __init__(self, acc_token: str, x_super: str, useragent: str, cookies, proxies) -> None:
        self.token = acc_token
        self.running = True
        self.x_super = x_super
        self.ua = useragent
        self.cookies = cookies
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
        
        self.ws.connect('wss://gateway.discord.gg/?encoding=json&v=9&compress=zlib-stream', headers= headers, host = "gateway.discord.gg", cookies = self.cookies, http_proxy_host=proxy_host, http_proxy_port=proxy_port, proxy_type="http", http_proxy_auth = proxy_auth)
       
        interval = self.recieve()['d']['heartbeat_interval'] / 1000
        threading.Thread(target=self.heartbeat, args=(interval, ), daemon=True).start()

    def online(self):
        payload = utils.getWebsocketData(self.token, self.x_super)
        print(payload)
        self.send_payload(payload)
        time.sleep(3)
        self.send_payload({"op":4,"d":{"guild_id":None,"channel_id":None,"self_mute":True,"self_deaf":False,"self_video":False,"flags":2}})

    def run(self):
        self.login()
        self.online()
        time.sleep(random.randint(20, 40))
        self.running = False