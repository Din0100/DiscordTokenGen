import requests
from custom_exceptions import no_session, captcha_error
from config import capmonster_key
import time

class capmonster_hcap():
    def __init__(self, site_key, proxy=False, session=None, website_url = "https://discord.com/"):
        self.site_key = site_key
        self.proxy = proxy
        self.session = session
        self.url = website_url
        if self.proxy == True and self.session == None:
            raise no_session
        
    def solve_captcha(self):
        captcha_payload = {
            "clientKey": capmonster_key,
            "task":{
                "type":"HCaptchaTaskProxyless",
                "websiteURL": self.url,
                "websiteKey": self.site_key,
            }   
        }
        
        if self.proxy == True:
            try:
                proxy = self.session.proxies['http'].replace("http://", "")
                captcha_payload['task']['proxyAddress'] = proxy.split("@")[1].split(":")[0]
                captcha_payload['task']['proxyPort'] = proxy.split("@")[1].split(":")[1]
                captcha_payload['task']['proxyLogin'] = proxy.split("@")[0].split(":")[0]
                captcha_payload['task']['proxyPassword'] = proxy.split("@")[0].split(":")[1]
                
                captcha_payload["task"]["type"] = "HCaptchaTask"
            except:
                pass
            
        r = requests.post(f"https://api.capmonster.cloud/createTask",json=captcha_payload)
        try:
            if r.json().get("taskId"):
                self.taskid = r.json()["taskId"]
                self.check_captcha()
                return self.key
            else:
                raise captcha_error
        except:
            raise captcha_error
            
    def check_captcha(self):
        payload = {
            "clientKey" : capmonster_key,
            "taskId" : self.taskid
        }
        
        got_captcha = False
        time.sleep(10)
        while got_captcha == False:
            try:
                r = requests.post(f"https://api.capmonster.cloud/getTaskResult",json=payload)
                if r.json()["status"] == "ready":
                    self.key = r.json()["solution"]["gRecaptchaResponse"]
                    self.ua = r.json()["solution"]["userAgent"]
                    got_captcha = True
                elif r.json()['status'] == "failed":
                    raise captcha_error
                time.sleep(2)
            except:
                if "ERROR_NO_SLOT_AVAILABLE" in r.text:
                    print("Retrying captcha")
                    time.sleep(3)
                    self.solve_captcha()
                else:
                    raise captcha_error