import tls_client
import random
import utils
import custom_exceptions
from os import system
from captcha import capmonster_hcap
import names


register_sitekey = "4c672d35-0701-42b2-88c3-78380b0db560"
x_track = "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExMy4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTEzLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjk5OTksImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"

class mass_join():
    def __init__(self, task_id, proxies, user_agents, counter, catchall, inv_code = None):
        self.task_id = task_id
        self.proxies = proxies
        self.domain = catchall
        self.invite_code = inv_code
        self.user_agent = random.choice(user_agents)
        self.counter = counter
        self.num_attempts = 0
        
        self.username = utils.load_random_username()
        self.password = utils.random_string(12)
        
        self.session = tls_client.Session(
            client_identifier = utils.get_identifier(self.user_agent),
            random_tls_extension_order=True
        )
        
        self.session.headers["x-super-properties"] = utils.get_trackers(self.user_agent)
    
    def entrypoint(self):
        try:
            self.setup_session()
            self.register()
            self.counter.increment()
            return self.token
        except Exception as e:
            print(f"Error Generating token : {e}")
            return None
    
    def setup_session(self):
        cookie_headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": self.user_agent,
        }
        
        cookies_res = self.session.get("https://discord.com/app", headers=cookie_headers)      
        cookies_dict = cookies_res.cookies.get_dict()
        if cookies_dict == None:
            raise Exception
        self.cookies = "locale=US; " + "; ".join([str(x)+"="+str(y) for x,y in cookies_dict.items()])
        
        setup_headers = {
            "accept": "*/*",
            "accept-encoding": "hi",
            "accept-language": "en-US,en;q=0.9",
            "cookie": self.cookies,
            "referer": "https://discord.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": self.user_agent,
            "x-track" : x_track
        }
        
        fingerprint_res = self.session.get("https://discord.com/api/v9/experiments", headers = setup_headers)
        try:
            self.fingerprint = fingerprint_res.json()["fingerprint"]
        except:
            raise custom_exceptions.cookie_or_fingerprint_exception
    
        
    def register(self):
        self.email = f'{names.get_full_name().replace(" ", "")}{random.randint(1000,9999)}@{self.domain}'
        register_url = "https://discord.com/api/v9/auth/register"
      
        register_payload = {
            'fingerprint': self.fingerprint,
            'email': self.email,
            'username': self.username,
            'password': self.password, 
            'invite': self.invite_code,
            'consent': "true",
            'date_of_birth': utils.GenerateBornDate(),
            'gift_code_sku_id': None,
            "captcha_key": str(capmonster_hcap(proxy=True,site_key=register_sitekey, session=self.session, website_url=register_url).solve_captcha()), 
            "promotional_email_opt_in": False
        }
        
        register_headers = {
            "accept": "*/*",
            "accept-encoding": "hi",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "cookie": self.cookies,
            'authorization': self.token,
            "origin": "https://discord.com",
            "referer": "https://discord.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": self.user_agent,
            "x-fingerprint": self.fingerprint,
            "x-debug-options": "bugReporterEnabled",
            "x-track": x_track,
        }
        
        register_res = self.session.post(register_url, headers = register_headers, json = register_payload)
        if "invalid-response" in register_res.text:
            self.register()
        
        if 'token' not in register_res.text:
            raise custom_exceptions.token_gen_failure
        
        self.token = register_res.json()["token"]