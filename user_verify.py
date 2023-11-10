from kopeechka import MailActivations
import kopeechka
from smsactivate.api import SMSActivateAPI
from custom_exceptions import mail_error, sms_timeout, sms_error
import time
import sys
import config
import utils
from currency_converter import CurrencyConverter
from currency_symbols import CurrencySymbols
import requests

c = CurrencyConverter()
body = MailActivations(token=config.email_api_key)
sa = SMSActivateAPI(config.sms_api_key)

try:
    cur_symbol = CurrencySymbols.get_symbol(config.currency)
except:
    cur_symbol = "$"

class SMSactivateHandler():
    @staticmethod
    def get_balance():
        balance = sa.getBalance()["balance"]
        local_amount = round(c.convert(balance, "RUB", config.currency), 2)
        if float(local_amount) < config.warning_amount:
            selection = input(f"WARNING: SMSActivate balance is {balance} Rubles ({cur_symbol}{local_amount}), would you like to continue anyway (Y/N) ")
            if selection.lower() == "y":
                utils.clear()
                pass
            else:
                sys.exit()
        else:
            if config.see_balance:
                print(f"SMSActivate balance is {balance} Rubles ({cur_symbol}{local_amount})")
        
    @staticmethod
    def get_number(cc = 16):
        return sa.getNumber(service="ds", freePrice=False, country=cc)
    
    @staticmethod
    def check_status(num_object):
        t_end = time.time() + 60
        while time.time() < t_end:
            status = sa.getStatus(str(num_object["activation_id"]))
            if status == "STATUS_WAIT_CODE":
                time.sleep(3)
            elif "STATUS_OK" in status:
                return status.split(":")[1]
            else:
                raise sms_error
        else:
            raise sms_timeout


class kopeechkaHandler():
    @staticmethod
    def check_balance():
        balance = body.user_balance()
        local_amount = round(c.convert(balance.balance, "RUB", new_currency=config.currency), 2)
        if int(local_amount) < config.warning_amount:
            selection = input(f"WARNING: Kopeetcha balance is {balance.balance} Rubles ({cur_symbol}{local_amount}), would you like to continue anyway (Y/N) ")
            if selection.lower() == "y":
                utils.clear()
                pass
            else:
                sys.exit()
        else:
            if config.see_balance:
                print(f"Kopeechka balance is {balance.balance} Rubles ({cur_symbol}{local_amount})")
    
    @staticmethod
    def get_email_link():
        data = body.mailbox_get_email(site="discord.com", mail_type="OUTLOOK", sender="noreply@discord.com", regex="", soft_id=0, investor=0, subject="", clear=1)
        if data.status == "OK":
            return data.data
        else:
            return False
    
    @staticmethod
    def get_message(id):
        attempt = 0
        while attempt < 5:
            time.sleep(5)
            try:
                data = body.mailbox_get_message(full=0, id=id)
                return data.value
            except kopeechka.errors.wait_link.WAIT_LINK:
                attempt += 1
            except:
                raise mail_error
            
    @staticmethod
    def get_top_countries():
        res = requests.get(f"https://api.sms-activate.org/stubs/handler_api.php?api_key=${config.sms_api_key}&action=getTopCountriesByService&service=$ds")
        print(res.json())
                
            
class fiveSimHandler():
    @staticmethod
    def get_number():
        country = 'england'
        operator = 'three'
        product = 'discord'

        headers = {
            'Authorization': 'Bearer ' + config.fivesim_api_key,
            'Accept': 'application/json',
        }

        num_res = requests.get('https://5sim.net/v1/user/buy/activation/' + country + '/' + operator + '/' + product, headers=headers)
        print(num_res.text)
        fiveSimHandler.check_status(num_res.json()["id"])
        return num_res.json()
    
    @staticmethod
    def check_status(id):
        while True:
            headers = {
                'Authorization': 'Bearer ' + config.fivesim_api_key,
                'Accept': 'application/json',
            }
            
            response = requests.get('https://5sim.net/v1/user/check/' + str(id), headers=headers)
            status = response.json()["status"]
            print(response.json())
            time.sleep(5)
            
    
    @staticmethod
    def get_code(num_dict):
        headers = {
            'Authorization': 'Bearer ' + config.fivesim_api_key,
            'Accept': 'application/json',
        }
        id = num_dict["id"]
        t_end = time.time() + 60
        while time.time() < t_end:
            response = requests.get('https://5sim.net/v1/user/check/' + str(id), headers=headers)
            response.raise_for_status()
            res_json = response.json()
            if res_json["status"] == "RECEIVED":
                try:
                    response = requests.get('https://5sim.net/v1/user/finish/' + str(id), headers=headers)
                    print(response)
                    return res_json["sms"][0]["code"]
                except:
                    pass
            time.sleep(5)
        else:
            raise sms_timeout
