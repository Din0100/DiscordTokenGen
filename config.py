script_name = "Discord Toolbox"

# api keys
email_api_key = ""
sms_api_key = ""
capmonster_key = ""
fivesim_api_key = ""

# tasks config
threads = 10
invite_code = None #This should usually be None, raiding function will specifically ask for an inv code, this only applies for verified token gen
real_usernames = True
add_pfp = True
add_bio = False # not implemented yet
catchall = "examplecatchall.com" #This is for raiding as it will generate unverified tokens, but they will join anyway.
tokens_online = False #Set this to true if you want any tokens you put in tokens_online to bet set to online while the script runs (Not implemented yet)

# Misc - random QOL improvments (mostly not needed, was just bored)
warning_amount = 1 #When the script starts it will warn you if your email or SMS accounts are bellow this USD amount
see_balance = True #prints the balance of your email and sms at the start of the script - suggest keeping to True
currency = "USD" #use whatever is local to you
logging = True #True means detailed logs, False means just a "running..." message with total tokens genned in the cmd/terminal title.

#advanced - unlikely to need changing
batch_size = 2000
websocket_online_period = 180 #this is in seconds, set to 0 for running forever, not recommended with large amounts of tokens as threading issues may occur