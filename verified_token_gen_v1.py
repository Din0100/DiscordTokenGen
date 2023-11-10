import tls_client
import requests
import json
import random
import utils
import custom_exceptions as exceptions
import tls_client.exceptions as tls_exceptions
import names
from captcha import capmonster_hcap
from discord_websocket import DiscordWs
from discord_websocket_v1 import DiscordWs_v1
import time
import threading
from user_verify import kopeechkaHandler, SMSactivateHandler
import config

x_track = "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExMy4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTEzLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjk5OTksImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
register_sitekey = "4c672d35-0701-42b2-88c3-78380b0db560"
verify_sitekey = "f5561ba9-8f1e-40ca-9b5b-a0b3f719ef34"
identifiers = ['safari_ios_16_0', 'safari_ios_15_6', 'safari_ios_15_5', 'safari_16_0', 'safari_15_6_1', 'safari_15_3', 'opera_90', 'opera_89', 'firefox_104', 'firefox_102']

class token_generator_v1():
    def __init__(self, proxies, task_id, username_type = "real", invite_code = None) -> None:
        self.task_id = task_id
        self.proxies = proxies
        self.inv = invite_code
        self.session_properties = utils.get_random_properties()
        self.username = utils.load_random_username()
        self.password = utils.random_string(12)
        self.session = tls_client.Session(
            ja3_string = self.session_properties["ja3"],
            client_identifier = random.choice(identifiers),
        )
        self.rotate_proxy()
        self.session.headers["user-agent"] = self.session_properties["useragent"]
        
    def entrypoint(self):
        self.logger("Generating token...")
        try:
            self.get_cookies()
            self.get_fingerprint()
            self.register()
            threading.Thread(target = DiscordWs_v1(self.token, self.session_properties["x-super-properties"], self.session_properties["useragent"], cookies=self.cookies, proxies=self.session.proxies).run, daemon=True).start()
            self.verify_email()
            self.verify_number()
            self.logger(f"Generated verified token {self.token}", "success")
            utils.write_success(self.token, "verified")
            return self.token
        except Exception as e:
            self.logger(f"Error generating token, trying again... ({e})")
            return None
        
    def get_cookies(self):
        get_cookies_headers = {
            'authority': 'discord.com',
            'accept': '*/*',
            'accept-language': 'en-GB,en;q=0.9',
            'referer': 'https://discord.com/',
            'sec-ch-ua': '"Google Chrome";v="112", "Chromium";v="112", "Not-A.Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            "user-agent": self.session_properties["useragent"],
        }
        
        cookies_res = self.session.get("https://discord.com/app", headers=get_cookies_headers)      
        cookies_dict = cookies_res.cookies.get_dict()
        if cookies_dict == None:
            raise Exception
        self.cookies = "locale=US; " + "; ".join([str(x)+"="+str(y) for x,y in cookies_dict.items()])
        self.logger("Got Cookies")
        
    def get_fingerprint(self):
        get_fingerprint_headers = {
            "accept": "*/*",
            "accept-encoding": "hi",
            "accept-language": "en-US,en;q=0.9",
            "cookie": self.cookies,
            "referer": "https://discord.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": self.session_properties["useragent"],
        }
        
        fingerprint_res = self.session.get("https://discord.com/api/v9/experiments", headers = get_fingerprint_headers)
        try:
            self.fingerprint = fingerprint_res.json()["fingerprint"]
        except:
            raise exceptions.cookie_or_fingerprint_exception
        
        self.logger("Got fingerprint")
        
    def register(self):
        email_obj = kopeechkaHandler.get_email_link()
        self.email = email_obj["mail"]
        self.email_id = email_obj["id"]
        
        captcha_token = capmonster_hcap(proxy=True,site_key="4c672d35-0701-42b2-88c3-78380b0db560", session=self.session, website_url="https://discord.com/api/v9/auth/register").solve_captcha()
        payload = {
            'fingerprint': self.fingerprint,
            'email': self.email,
            'username': self.username,
            'password': self.password, 
            'invite': self.inv,
            'consent': True,
            'date_of_birth': utils.GenerateBornDate(),
            'bio': ".gg/23bp", 
            'gift_code_sku_id': None,
            "captcha_key": str(captcha_token), 
            "promotional_email_opt_in": False
        }
        
        headers = {
            'Host': 'discord.com',
            'User-Agent': self.session_properties["useragent"],
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cookie' : self.cookies,
            'Content-Type': 'application/json',
            'X-Super-Properties': self.session_properties["x-super-properties"],
            'X-Fingerprint': self.fingerprint,
            'X-Discord-Locale': 'en-US',
            'X-Debug-Options': 'bugReporterEnabled',
            'Origin': 'https://discord.com',
            'Alt-Used': 'discord.com',
            'Connection': 'keep-alive',
            'Referer': 'https://discord.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'dnt': '1',
            'TE': 'trailers'
        }
        
        try:
            register_res = self.session.post("https://discord.com/api/v9/auth/register", headers=headers, json=payload)
            if "invalid-response" in register_res.text:
                self.register()
            
            if 'token' not in register_res.text:
                raise exceptions.token_gen_failure
            
            self.token = register_res.json().get('token')
            self.logger("Registered Account", "success")
        except Exception as e:
            self.logger(e, "error")
            raise exceptions.token_gen_failure
        
    def verify_email(self):
        try:
            redirect_url = self.session.get(kopeechkaHandler.get_message(id=self.email_id), allow_redirects = True).url
            email_token = redirect_url.split("token=")[1]
        except tls_exceptions.TLSClientExeption:
            try:
                self.verify_number()
                self.verify_email()
            except:
                raise exceptions.token_gen_failure
        except:
            raise exceptions.token_gen_failure
            
        captcha_token = capmonster_hcap(proxy=True, session=self.session, site_key=verify_sitekey, website_url=redirect_url).solve_captcha()
        
        email_headers = {
            'Host': 'discord.com',
            'User-Agent': self.session_properties["useragent"],
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Cookie' : self.cookies,
            'X-Super-Properties': self.session_properties["x-super-properties"],
            'X-Fingerprint': self.fingerprint,
            'X-Discord-Locale': 'en-US',
            'authorization': self.token,
            'X-Debug-Options': 'bugReporterEnabled',
            'Origin': 'https://discord.com',
            'Alt-Used': 'discord.com',
            'Connection': 'keep-alive',
            'Referer': 'https://discord.com/verify',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'dnt': '1',
            'TE': 'trailers'
		}
        
        email_payload = {
            "token": email_token,
            "captcha_key": captcha_token
        }
        
        verify_response = self.session.post("https://discord.com/api/v9/auth/verify", headers=email_headers, json=email_payload)
        
        if "TOKEN_INVALID" in verify_response.text:
            raise exceptions.token_gen_failure
        if verify_response.status_code == 200:
            if self.token != verify_response.json()["token"]:
                raise exceptions.token_gen_failure
            self.logger("Verified email", "success")
            return
        else:
            raise exceptions.token_gen_failure
            
    def verify_number(self):
        valid = self.send_phone_verification()
        if valid == False:
            raise Exception
        self.post_number_code()
        self.post_final_number()
        self.logger("Verified Number", "success")
        
    def send_phone_verification(self, cc = 16 ):
        pending = True
        attempts = 0
        while pending:
            url = "https://discord.com/api/v9/users/@me/phone"
            
            number_cap_token = capmonster_hcap(proxy=True, session=self.session, site_key="f5561ba9-8f1e-40ca-9b5b-a0b3f719ef34", website_url="https://discord.com/api/v9/users/@me/phone").solve_captcha()
            
            self.number_dict = SMSactivateHandler.get_number(cc)
            
            payload = json.dumps({
                "phone": f"+{self.number_dict['phone']}",
            })
            
            headers = {
                'Host': 'discord.com',
                'x-super-properties': self.session_properties["x-super-properties"],
                'x-captcha-key': number_cap_token,
                'x-debug-options': 'bugReporterEnabled',
                'sec-ch-ua-mobile': '?0',
                'authorization': self.token,
                'user-agent': self.session_properties["useragent"],
                'content-type': 'application/json',
                'x-discord-locale': 'en-US',
                'sec-ch-ua-platform': '"Windows"',
                'accept': '*/*',
                'sec-gpc': '1',
                'origin': 'https://discord.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://discord.com/channels/@me',
                'accept-language': 'en-US,en;q=0.9',
                'dnt': '1',
            }
            
            res = self.session.post(url, headers=headers, data=payload, allow_redirects = True)
            if "401" in res.text:
                return False
            elif "Invalid phone number" in res.text or "VoIP" in res.text or "captcha"  in res.text:
                if attempts > 3:
                    return False
                else:
                    attempts += 1
            else:
                pending = False
        
    def post_number_code(self):
        url = "https://discord.com/api/v9/phone-verifications/verify"
        
        verification_code = SMSactivateHandler.check_status(self.number_dict)
        
        payload = json.dumps({
            "phone": f"+{str(self.number_dict['phone']).strip()}",
            "code": verification_code
        })
        
        
        headers = {
            'Host': 'discord.com',
            'User-Agent': self.session_properties["useragent"],
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'authorization': self.token,
            'Content-Type': 'application/json',
            'Cookie' : self.cookies,
            'X-Super-Properties': self.session_properties["x-super-properties"],
            'X-Fingerprint': self.fingerprint,
            'X-Discord-Locale': 'en-US',
            'X-Debug-Options': 'bugReporterEnabled',
            'Origin': 'https://discord.com',
            'Alt-Used': 'discord.com',
            'Connection': 'keep-alive',
            'Referer': 'https://discord.com/channels/@me',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'dnt': '1',
            'TE': 'trailers'
        }
        
        res = self.session.post(url, headers=headers, data=payload, allow_redirects = True)
        try:
            self.phone_token = res.json()["token"]
        except:
            raise Exception


    def post_final_number(self):
        url = "https://discord.com/api/v9/users/@me/phone"

        payload = json.dumps({
            "phone_token": self.phone_token,
            "password": self.password,
            # "change_phone_reason": "user_action_required"
        })
    
        headers = {
            'Host': 'discord.com',
            'User-Agent': self.session_properties["useragent"],
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'authorization': self.token,
            'Content-Type': 'application/json',
            'Cookie' : self.cookies,
            'X-Super-Properties': self.session_properties["x-super-properties"],
            'X-Fingerprint': self.fingerprint,
            'X-Discord-Locale': 'en-US',
            'X-Debug-Options': 'bugReporterEnabled',
            'Origin': 'https://discord.com',
            'Alt-Used': 'discord.com',
            'Connection': 'keep-alive',
            'Referer': 'https://discord.com/channels/@me',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'dnt': '1',
            'TE': 'trailers'
        }
        
        res = self.session.post(url, headers=headers, data=payload, allow_redirects = True)
        
    def change_pfp(self):
        payload = {
            "avatar" : utils.get_random_pfp()
        }
        
        headers = {
            "accept": "*/*",
            "accept-encoding": "none",
            "accept-language": "en-US",
            'user-agent' : self.session_propertien["useragent"],
            "authorization": self.token,
            "content-type": "application/json",
            "cookie": self.cookies,
            "origin": "https://discord.com",
            "referer": "https://discord.com/channels/@me",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": self.session_properties["useragent"],
            "x-debug-options": "bugReporterEnabled",
            "x-super-properties" : self.session_properties["x-super-properties"]
        }
        
        res = self.session.patch("https://discord.com/api/v9/users/@me", headers=headers, json=payload)
        if "401"  in res.text:
            raise exceptions.token_gen_failure
        elif res.status_code != 200:
            # something went wrong with changing the pfp
            pass
        
    def change_bio(self):
        payload = {
            "bio" : utils.generate_discord_bio()
        }
        
        headers = {
            "accept": "*/*",
            "accept-encoding": "none",
            "accept-language": "en-US",
            "authorization": self.token,
            "content-type": "application/json",
            "cookie": self.cookies,
            "origin": "https://discord.com",
            "referer": "https://discord.com/channels/@me",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": self.session_properties["useragent"],
            "x-debug-options": "bugReporterEnabled",
            "x-super-properties" : self.session_properties["x-super-properties"]
        }
        
        res = self.session.patch("https://discord.com/api/v9/users/@me", headers=headers, json=payload)
        if "401"  in res.text:
            raise exceptions.token_gen_failure
        elif res.status_code != 200:
            # something went wrong with changing the pfp
            pass
        
    def rotate_proxy(self):
        '''
        Randomly selects a proxy from self.proxies and assigns to self.proxy
        Then assigns self.proxy to session proxies
        run this function during session configuration to use proxies
        '''
        try:
            self.proxy = random.choice(self.proxies)
        except:
            # Likely no proxies loaded, script will run without proxies
            self.proxy = None
            
        self.session.proxies = self.proxy
        
    def logger(self, text, status="default"):
        ''' 
        Logs text to the terminal with task_id in log
        :params:
            text : message to log to terminal
            status : string to indicate what icon - exclude for [-]
        '''
        if config.logging:
            if status == "error":
                status_indicator = "[!]"
            elif status == "warning":
                status_indicator = "[⚠]"
            elif status == "fatal":
                status_indicator = "[☠]"
            elif status == "success":
                status_indicator = "[✓]"
            else:
                status_indicator = "[-]"
            
            print(f"[Task {self.task_id}]{status_indicator} - {text}")
        