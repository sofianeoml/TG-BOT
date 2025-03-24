from info import *
from library import *

db = MongoClient(db_url)
db = db["otpbot"]
users = db["users"]
keys = db["keys"]
spoof_db = db["spoofdb"]
calls_db = db["calls"]
recall_db = db["recall"]

twilio_client = Client(account_sid, auth_token)

app = Flask(__name__)
bot = telebot.TeleBot(telegram_bot_token, threaded=True)
bot.remove_webhook()
bot.set_webhook(url=ngrok_url)