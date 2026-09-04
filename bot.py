import requests
import schedule
import time
from telegram import Bot
from telegram.error import TelegramError
import os

# --- تنظیمات از متغیرهای محیطی (برای امنیت) ---
BOT_TOKEN = os.environ.get("1576429693:b2bpBk96A-rjcaUGr2gyeUFBy1WD1BGMw4o")   # توکن جدید رو اینجا بذار
GROUP_CHAT_ID = os.environ.get("5148513731") # 5148513731

def get_dollar_price():
    """
    دریافت قیمت فروش دلار از API
    """
    # آدرس API خودتون رو اینجا بذارید (مثلاً از BrsApi یا هر جای دیگه)
    url = "https://api.alanchand.com/?type=currencies&token=zrxEinn7OBmqHjoGDhxZ"  
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # استخراج قیمت فروش دلار از کلید usd -> sell
        dollar_info = data.get("usd")
        if dollar_info:
            sell_price = dollar_info.get("sell")
            updated_at = dollar_info.get("updated_at")
            
            if sell_price:
                return {
                    "price": sell_price,
                    "time": updated_at
                }
        
        print("خطا: داده‌های دلار پیدا نشد")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"خطا در ارتباط با API: {e}")
        return None
    except ValueError as e:
        print(f"خطا در پردازش JSON: {e}")
        return None

def send_price_update():
    """دریافت قیمت و ارسال به گروه"""
    print("در حال دریافت قیمت دلار...")
    result = get_dollar_price()
    
    if result:
        price = result["price"]
        time_updated = result["time"]
        
        message = f"💵 قیمت فروش دلار آمریکا:\n{price:,} تومان\n🕐 {time_updated}"
        
        try:
            bot = Bot(token=BOT_TOKEN)
            bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
            print("✅ پیام ارسال شد.")
        except TelegramError as e:
            print(f"❌ خطا در ارسال به تلگرام: {e}")
    else:
        error_message = "⚠️ خطا در دریافت قیمت دلار. لطفاً بعداً تلاش کنید."
        try:
            bot = Bot(token=BOT_TOKEN)
            bot.send_message(chat_id=GROUP_CHAT_ID, text=error_message)
        except TelegramError as e:
            print(f"❌ خطا در ارسال پیام خطا: {e}")

# --- برنامه‌ریزی هر ۱ ساعت ---
schedule.every(1).hours.do(send_price_update)

# --- ارسال یک بار در شروع ---
send_price_update()

print("✅ ربات با موفقیت شروع به کار کرد. هر ۱ ساعت قیمت ارسال می‌شود.")

# --- حلقه بی‌نهایت برای اجرای برنامه‌ریزی ---
while True:
    schedule.run_pending()
    time.sleep(1)