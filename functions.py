from library import *
from info import *
from connection import * 

# convert milliseconds to days,hours,minutes,seconds

def ms_to_dhms(milliseconds):
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return days, hours, minutes, seconds

# convert milliseconds to datetime

def milliseconds_to_datetime(milliseconds):
    # Convert milliseconds to seconds
    seconds = int(milliseconds) / 1000
    # Create a datetime object from the seconds
    date = datetime.utcfromtimestamp(seconds)
    return date

# convert days,hours,minutes,seconds to milliseconds

def dhms_to_ms(days, hours, minutes, seconds):
    milliseconds = (days * 24 * 60 * 60 + hours * 60 * 60 + minutes * 60 + seconds) * 1000
    return milliseconds

# show key plan message for telegram bot

def show_key_plan(key_plan):
    days, hours, minutes, seconds = ms_to_dhms(key_plan)
    if days == 0:
        if hours == 0:
            if minutes == 0:
                if seconds == 0:
                    msg = f'{seconds} Seconds'
                else:
                    msg = f'{seconds} Seconds'
            else:
                msg = f'{minutes} Minutes, {seconds} Seconds'
        else:
            msg = f'{hours} Hours, {minutes} Minutes, {seconds} Seconds'
    else:
        msg = f'{days} Days, {hours} Hours, {minutes} Minutes, {seconds} Seconds'
    return msg


# show user plan message for telegram bot

def show_user_plan(user_plan):
    if user_plan == 'No Plan':
        msg = user_plan
    else:
        days, hours, minutes, seconds = ms_to_dhms(user_plan)
        if days == 0:
            if hours == 0:
                if minutes == 0:
                    if seconds == 0:
                        msg = f'{seconds} Seconds'
                    else:
                        msg = f'{seconds} Seconds'
                else:
                    msg = f'{minutes} Minutes, {seconds} Seconds'
            else:
                msg = f'{hours} Hours, {minutes} Minutes, {seconds} Seconds'
        else:
            msg = f'{days} Days, {hours} Hours, {minutes} Minutes, {seconds} Seconds'
    return msg

# generate key message  for telegram bot

def generate_msg(days, hours, minutes, seconds,code,linked):
    if days == 0:
        if hours == 0:
            if minutes == 0:
                if seconds == 0:
                    msg = f'✅ Successfully Added :\n  |   KEY : {code}\n  |   PLAN : {seconds} Seconds\n  |   LINKED : {linked}'
                else:
                    msg = f'✅ Successfully Added :\n  |   KEY : {code}\n  |   PLAN : {seconds} Seconds\n  |   LINKED : {linked}'
            else:
                msg = f'✅ Successfully Added :\n  |   KEY : {code}\n  |   PLAN : {minutes} Minutes, {seconds} Seconds\n  |   LINKED : {linked}'
        else:
            msg = f'✅ Successfully Added :\n  |   KEY : {code}\n  |   PLAN : {hours} Hours, {minutes} Minutes, {seconds} Seconds\n  |   LINKED : {linked}'
    else:
        msg = f'✅ Successfully Added :\n  |   KEY : {code}\n  |   PLAN : {days} Days, {hours} Hours, {minutes} Minutes, {seconds} Seconds\n  |   LINKED : {linked}'
    
    return msg

# checktime message for telegram bot

def checktime_msg(days, hours, minutes, seconds,user_plan):
    days = days
    hours = hours
    minutes = minutes
    seconds = seconds
    day, hour, minute, second = ms_to_dhms(int(user_plan))
    if day == 0:
        if hour == 0:
            if minute == 0:
                if second == 0:
                    user_plan = f'{second} Seconds'
                else:
                    user_plan = f'{second} Seconds'
            else:
                user_plan = f'{minute} Minutes, {second} Seconds'
        else:
            user_plan = f'{hour} Hours, {minute} Minutes, {second} Seconds'
    else:
        user_plan = f'{day} days, {hour} Hours, {minute} Minutes, {second} Seconds'

    if days == 0:
        if hours == 0:
            if minutes == 0:
                if seconds == 0:
                    msg = f'✅ Plan Active :\n  |   Plan : {user_plan} \n  |   Time Left : {seconds} Seconds'
                else:
                    msg = f'✅ Plan Active :\n  |   Plan : {user_plan} \n  |   Time Left : {seconds} Seconds'
            else:
                msg = f'✅ Plan Active :\n  |   Plan : {user_plan} \n  |   Time Left : {minutes} Minutes, {seconds} Seconds'
        else:
            msg = f'✅ Plan Active :\n  |   Plan : {user_plan} \n  |   Time Left : {hours} Hours, {minutes} Minutes, {seconds} Seconds'
    else:
        msg = f'✅ Plan Active :\n  |   Plan : {user_plan} \n  |   Time Left : {days} Days, {hours} Hours, {minutes} Minutes, {seconds} Seconds'
    return msg

# reddem message for telegram bot

def redeem_msg(days, hours, minutes, seconds,key_plan):
    days = days
    hours = hours
    minutes = minutes
    seconds = seconds
    if days == 0:
        if hours == 0:
            if minutes == 0:
                if seconds == 0:
                    msg = f'✅ Key Activated :\n  |   KEY : {key_plan}\n  |   Plan : {seconds} Seconds'
                else:
                    msg = f'✅ Key Activated :\n  |   KEY : {key_plan}\n  |   Plan : {seconds} Seconds'
            else:
                msg = f'✅ Key Activated :\n  |   KEY : {key_plan}\n  |   Plan : {minutes} Minutes, {seconds} Seconds'
        else:
            msg = f'✅ Key Activated :\n  |   KEY : {key_plan}\n  |   Plan : {hours} Hours, {minutes} Minutes, {seconds} Seconds'
    else:
        msg = f'✅ Key Activated :\n  |   KEY : {key_plan}\n  |   Plan : {days} Days, {hours} Hours, {minutes} Minutes, {seconds} Seconds'
    return msg

# generate random key 

def generate_key():
    fixed_part = "1X-SEC-OTP-"
    
    # Generate four groups of 5 random characters each
    groups = [
        ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        for _ in range(4)
    ]

    # Combine the fixed part and groups to create the final key
    key = fixed_part + '-'.join(groups)

    return key

def download_recording(recording_url, file_name):
    """Download the recording from Twilio and save it as an MP3 file."""
    max_retries = 5  # Maximum number of retries
    retry_delay = 2  # Delay between retries (in seconds)

    for attempt in range(max_retries):
        try:
            # Add authentication using Twilio credentials
            auth = (account_sid, auth_token)
            response = requests.get(recording_url, auth=auth)
            response.raise_for_status()  # Raise an error for bad status codes

            # Save the recording as an MP3 file
            with open(file_name, "wb") as file:
                file.write(response.content)
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404 and attempt < max_retries - 1:
                # Wait and retry if the recording is not found
                print(f"Recording not found. Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print(f"Failed to download recording: {e}")
                return False
    return False

def send_recording_to_telegram(file_path, chat_id):
    """Send the recording file to a Telegram user."""
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendAudio"
    with open(file_path, "rb") as audio_file:
        files = {"audio": audio_file}
        data = {"chat_id": chat_id}
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("Recording sent to Telegram successfully.")
            return True
        else:
            print(f"Failed to send recording to Telegram: {response.text}")
            return False