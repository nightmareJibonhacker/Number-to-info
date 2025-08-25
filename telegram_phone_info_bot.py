import telebot
import requests

TELEGRAM_BOT_TOKEN = '7807772456:AAGJ3PE6EiWpe6m6b2BZhfDP83scDRo61ik'
NUMVERIFY_API_KEY = '7a07c94fe9849869c8ffc96ee0022d53'
GEOCODING_API_URL = 'https://nominatim.openstreetmap.org/search'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def get_phone_info(phone_number):
    url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={phone_number}"
    try:
        response = requests.get(url)
        data = response.json()
        if data['valid']:
            info = {
                "number": data['international_format'],
                "country": data['country_name'],
                "country_code": data['country_code'],
                "location": data['location'],
                "carrier": data['carrier'],
                "type": data['line_type'],
            }
        else:
            info = None
    except Exception as e:
        info = None
    return info

def get_geocode(location, country):
    params = {
        'q': f"{location}, {country}",
        'format': 'json'
    }
    try:
        response = requests.get(GEOCODING_API_URL, params=params)
        data = response.json()
        if data and len(data) > 0:
            lat = data[0]['lat']
            lon = data[0]['lon']
            return lat, lon
        else:
            return None, None
    except Exception as e:
        return None, None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "হ্যালো! ফোন নাম্বার দিন (দেশ কোড সহ)।\nউদাহরণ: +8801712345678")

@bot.message_handler(func=lambda message: True)
def handle_phone_number(message):
    phone_number = message.text.strip()
    info = get_phone_info(phone_number)
    if info:
        lat, lon = get_geocode(info['location'], info['country'])
        reply = f"""
নাম্বার: {info['number']}
দেশ: {info['country']}
কোড: +{info['country_code']}
লোকেশন: {info['location']}
ক্যারিয়ার: {info['carrier']}
টাইপ: {info['type']}
"""
        if lat and lon:
            reply += f"জিও কোড: Latitude: {lat}, Longitude: {lon}\n"
            reply += f"Google Map: https://www.google.com/maps/search/?api=1&query={lat},{lon}\n"
        else:
            reply += "লোকেশনের জিও কোড পাওয়া যায়নি।"
    else:
        reply = "নাম্বারটি সঠিক নয়, আবার চেষ্টা করুন!"
    bot.reply_to(message, reply)

if __name__ == '__main__':
    print("Bot is running...")
    bot.polling()
