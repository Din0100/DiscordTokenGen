import threading
import utils
import threading
from verified_token_gen import verifiedTokenGenerator
from verified_token_gen_v1 import token_generator_v1
import tools.raid_functions as raid_funcs
from tools.token_online import DiscordOnlineWebsocket
from tools.vc_spam import vc_spam
import time
import config
from unverified_mass_join import mass_join
import concurrent.futures
import random
import os
# from simple_term_menu import TerminalMenu
import sys

write_lock = threading.Lock()
user_agents = utils.load_useragents()
counter = 0

def main():
    utils.print_title()
    tokens = utils.load_tokens()
    options = ["Generate Valid Tokens", "Channel Spam", "Mass React","Mass Report", "Channel Raid", "Online Tokens", "Format Pfps"]
    print("\nSelect an option")
    # term_menu = TerminalMenu(options)
    # task_index = term_menu.show()
    for index, option in enumerate(options):
        print(f"{index} - {option}")
    task_index = input()
    try:
        utils.clear()
        if task_index == 0:
            run_token_gen()
            # token_generator_v1()
        elif task_index == 1 or task_index == 2 or task_index == 3:
            raid_funcs.async_task_handler(options[task_index-1], tokens)
        elif task_index == 4:
            run_token_gen()
        elif task_index == 5:
            online_manager()
        elif task_index == 6:
            print("This will take all pictures in data/unformatted_pfps and convert them into 128x128 to be used in the token gen.")
        else:
            raise Exception
    except:
        print("Invalid input")
        
def online_manager(tokens):
    utils.clear()
    print("Make sure all tokens you want online are in the online_tokens.txt")
    try:
        threads = int(input("Select how many threads :"))
    except:
        print("Invalid input")
        time.sleep(2)
        online_manager()
    proxies = utils.load_all_proxies()
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for token in tokens:
            futures.append(executor.submit(DiscordOnlineWebsocket(token, user_agents, proxies, period=config.websocket_online_period)))
        for future in concurrent.futures.as_completed(futures):
            pass
        
    print("All tokens have been online!")
            
def run_token_gen():
    proxies = utils.load_all_proxies()
    task_counter = utils.Counter(0)
    print("Starting Tasks...")
    counter_thread = threading.Thread(daemon=True, target=utils.update_title, args=(task_counter, )).start()
    for _ in range(config.threads):
        threading.Thread(target=thread_manager, args=(proxies,user_agents,task_counter, )).start()
            
def run_invite_gen():
    proxies = utils.load_all_proxies()
    invite_code = input("Invite Code (example : h9ZvF5zq)-> ")
    num_of_tasks = input("How many tasks would you like to run: ")
    try:
        task_count = int(num_of_tasks)
    except:
        print("Invalid input, try again...")
        time.sleep(2)
        utils.clear()
    task_counter = utils.Counter(0)
    task_id = 0
    counter_thread = threading.Thread(daemon=True, target=utils.update_title, args=(task_counter, )).start()
    with open("output/unverified_tokens.txt", "a", encoding="UTF-8") as f:
        with concurrent.futures.ThreadPoolExecutor(max_workers=config.threads) as executor:
            futures = []
            for x in range(task_count):
                task_id += 1
                futures.append(executor.submit(mass_join(proxies=proxies, task_id=task_id,catchall=config.catchall,user_agents=user_agents, counter = task_count, invite_code=invite_code).entrypoint))
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                try:
                    if type(res) == str:
                        with write_lock:
                            f.write(res + "\n")
                except:
                    pass
        
def thread_manager(proxies,user_agents, task_counter,):
    global counter
    while True:
        try:
            token_generator_v1(task_id=counter, proxies=proxies).entrypoint()
            counter += 1
        except Exception as e:
            print(e)
            print("Error running thread, exiting...")
            time.sleep(2)
            sys.exit()
            
def vc_spam_manager(tokens, file):
    utils.clear()
    try:
        token_amount = int(input("How many tokens: "))
    except:
        print("Invalid input")
        vc_spam_manager()
        
    audios = os.listdir("tools/audio")
    for idx, item in enumerate(audios):
        print(f"{idx} - {item}")
        
    index = int(input("Select an audio file:"))
    try:
        file_name = audios[index]
    except:
        print("Invalid input")
        vc_spam_manager()
    
    voice_id = input("Enter Voice Id: ")
        
    for i in range(len(token_amount)):
        threading.Thread(target=vc_spam, args=(random.choice(tokens), file_name, voice_id)).start()

if __name__ == "__main__":
    main()


