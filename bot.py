import os
import io
import time
import base64
import datetime
import requests
import subprocess
import threading
import edge_tts
import imageio_ffmpeg
from http.server import BaseHTTPRequestHandler, HTTPServer
from bs4 import BeautifulSoup
from html2image import Html2Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

# ================= কনফিগারেশন =================
TELEGRAM_BOT_TOKEN = "9147678230:AAHEqCRTOLiKDCrjfr9VDWtlinQxvJaDFGw"
MAKE_WEBHOOK_URL = "https://hook.eu1.make.com/8gpd5qyzdiobc85z6mre9xy56uto2gex"
WEBSITE_NAME = "moktokontho.com"
VOICE_NAME = "bn-BD-NabanitaNeural"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ক্লাউড লিনাক্স সার্ভারে ক্রোমিয়াম পাথ ও বিশেষ ফ্ল্যাগ
chrome_bin = "/usr/bin/chromium"
browser_exec = chrome_bin if os.path.exists(chrome_bin) else None
c_flags = ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']

hti_card = Html2Image(output_path=BASE_DIR, size=(1080, 1080), browser_executable=browser_exec, custom_flags=c_flags)
hti_reel = Html2Image(output_path=BASE_DIR, size=(1080, 1920), browser_executable=browser_exec, custom_flags=c_flags)

# ক্লাউড সার্ভার যেন ২৪ ঘণ্টা জীবিত থাকে তার জন্য হেলথ চেক সার্ভার
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Mokto Kontho News Bot 24/7 is Live!")
    def log_message(self, format, *args):
        return

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()
# ===============================================

def get_bangla_date():
    days = {0: "সোমবার", 1: "মঙ্গলবার", 2: "বুধবার", 3: "বৃহস্পতিবার", 4: "শুক্রবার", 5: "শনিবার", 6: "রবিবার"}
    months = {1: "জানুয়ারি", 2: "ফেব্রুয়ারি", 3: "মার্চ", 4: "এপ্রিল", 5: "মে", 6: "জুন", 
              7: "জুলাই", 8: "আগস্ট", 9: "সেপ্টেম্বর", 10: "অক্টোবর", 11: "নভেম্বর", 12: "ডিসেম্বর"}
    digits = {'0':'০', '1':'১', '2':'২', '3':'৩', '4':'৪', '5':'৫', '6':'৬', '7':'৭', '8':'৮', '9':'৯'}
    now = datetime.datetime.now()
    d_name = days[now.weekday()]
    d_num = "".join(digits.get(d, d) for d in str(now.day))
    m_name = months[now.month]
    y_num = "".join(digits.get(d, d) for d in str(now.year))
    return f"{d_name}, {d_num} {m_name} {y_num} ইং"

def scrape_news(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=20)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find("meta", property="og:title")
    image_url = soup.find("meta", property="og:image")
    title_text = title["content"] if title else (soup.title.string if soup.title else "খবরের শিরোনাম")
    img_url = image_url["content"] if image_url else ""
    return title_text.strip(), img_url

def create_card(image_url, title):
    img_src = image_url
    if image_url:
        try:
            r = requests.get(image_url, timeout=15)
            img_src = f"data:image/jpeg;base64,{base64.b64encode(r.content).decode()}"
        except:
            pass

    html = """<!DOCTYPE html><html><head><meta charset="utf-8">
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@600;700&display=swap');
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body { width: 1080px; height: 1080px; background: #990000; font-family: 'Hind Siliguri', sans-serif; position: relative; }
      .img-box { width: 1080px; height: 600px; background: #222; }
      .img-box img { width: 100%; height: 100%; object-fit: cover; }
      .title-box { height: 400px; display: flex; align-items: center; justify-content: center; padding: 20px 60px; text-align: center; }
      .title-box h1 { color: #fff; font-size: 52px; font-weight: 700; line-height: 1.35; }
      .footer { position: absolute; bottom: 0; left: 0; width: 1080px; height: 80px; border-top: 1.5px solid rgba(255,255,255,0.25); display: flex; justify-content: space-between; align-items: center; padding: 0 50px; color: #ffcdd2; font-size: 25px; }
      .footer .site { color: #fff; font-family: Arial; }
    </style></head><body>
      <div class="img-box"><img src="__IMG__"></div>
      <div class="title-box"><h1>__TITLE__</h1></div>
      <div class="footer"><div>__DATE__</div><div class="site">__SITE__</div></div>
    </body></html>"""
    
    html = html.replace("__IMG__", img_src).replace("__TITLE__", title).replace("__DATE__", get_bangla_date()).replace("__SITE__", WEBSITE_NAME)
    fname = f"card_{int(time.time())}.jpg"
    hti_card.screenshot(html_str=html, save_as=fname)
    return os.path.join(BASE_DIR, fname)

def create_reel_frame(image_url, title):
    img_src = image_url
    if image_url:
        try:
            r = requests.get(image_url, timeout=15)
            img_src = f"data:image/jpeg;base64,{base64.b64encode(r.content).decode()}"
        except:
            pass

    html = """<!DOCTYPE html><html><head><meta charset="utf-8">
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@600;700;800&display=swap');
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body {
        width: 1080px; height: 1920px;
        background: radial-gradient(circle at center, #260000 0%, #050000 100%);
        font-family: 'Hind Siliguri', sans-serif;
        display: flex; flex-direction: column; justify-content: space-between; align-items: center;
        padding: 80px 40px; position: relative; overflow: hidden;
      }
      .badge {
        background: linear-gradient(90deg, #d32f2f, #b71c1c);
        color: white; font-size: 36px; font-weight: 800;
        padding: 14px 45px; border-radius: 50px;
        letter-spacing: 2px;
      }
      .card {
        width: 1000px; background: #000; border-radius: 28px; overflow: hidden;
        border: 3px solid rgba(255,255,255,0.2);
      }
      .card img { width: 1000px; height: 920px; object-fit: cover; display: block; }
      .card .text {
        background: linear-gradient(180deg, #b71c1c 0%, #800000 100%);
        padding: 45px 35px; text-align: center;
        border-top: 4px solid #ffcc00;
      }
      .card .text h1 { color: #fff; font-size: 48px; font-weight: 800; line-height: 1.4; }
      .tag {
        color: #ffcdd2; font-size: 32px; font-weight: 600; text-align: center;
        background: rgba(0,0,0,0.6); padding: 15px 40px; border-radius: 50px;
      }
      .tag b { color: #ffcc00; }
    </style></head><body>
      <div class="badge">🔴 ব্রেকিং বুলেটিন</div>
      <div class="card">
        <img src="__IMG__">
        <div class="text"><h1>__TITLE__</h1></div>
      </div>
      <div class="tag">বিস্তারিত জানতে ভিজিট করুন: <b>__SITE__</b></div>
    </body></html>"""
    
    html = html.replace("__IMG__", img_src).replace("__TITLE__", title).replace("__SITE__", WEBSITE_NAME)
    fname = f"reel_frame_{int(time.time())}.jpg"
    hti_reel.screenshot(html_str=html, save_as=fname)
    return os.path.join(BASE_DIR, fname)

async def make_voice(title, out_path):
    script = f"মুক্তকণ্ঠের বিশেষ বুলেটিন। {title}। এ বিষয়ে বিস্তারিত খবর পড়তে এখনই ভিজিট করুন মুক্তকণ্ঠ ডট কমে।"
    comm = edge_tts.Communicate(script, VOICE_NAME, rate="-4%", pitch="+0Hz")
    await comm.save(out_path)

def make_cinematic_reel(frame_path, audio_path, out_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y",
        "-loop", "1", "-i", frame_path,
        "-i", audio_path,
        "-c:v", "libx264", "-preset", "ultrafast",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        out_path
    ]
    flags = 0x08000000 if os.name == 'nt' else 0
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags)
    return out_path

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("অনুগ্রহ করে খবরের সঠিক লিংক পাঠান।")
        return

    status = await update.message.reply_text("🔗 খবরটি পড়া হচ্ছে...")
    try:
        title, img_url = scrape_news(url)
        
        card_file = create_card(img_url, title)
        keyboard = [[InlineKeyboardButton("📘 ফেসবুকে পোস্ট করুন", callback_data="post_fb")]]
        
        caption_text = f"**{title}**\n\n🔗 খবরের লিংক:\n{url}"
        with open(card_file, 'rb') as photo:
            msg = await update.message.reply_photo(photo=photo, caption=caption_text, reply_markup=InlineKeyboardMarkup(keyboard))
            context.user_data['last_photo_id'] = msg.photo[-1].file_id

        try:
            await status.edit_text("🎬 রিলস ভিডিও তৈরি হচ্ছে...")
            audio_file = os.path.join(BASE_DIR, f"v_{int(time.time())}.mp3")
            await make_voice(title, audio_file)

            frame_file = create_reel_frame(img_url, title)
            video_file = os.path.join(BASE_DIR, f"reel_{int(time.time())}.mp4")
            make_cinematic_reel(frame_file, audio_file, video_file)

            with open(video_file, 'rb') as vid:
                await update.message.reply_video(
                    video=vid,
                    caption=f"🎬 **{title}**\n\n(রিলস ও শর্টসের জন্য প্রস্তুত!)",
                    supports_streaming=True
                )
        except Exception as v_err:
            print("Video error:", v_err)

        await status.delete()

    except Exception as e:
        await update.message.reply_text(f"সমস্যা হয়েছে: {str(e)}")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "post_fb":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("🚀 ফেসবুকে পোস্ট করা হচ্ছে, ৫-১০ সেকেন্ড অপেক্ষা করুন...")
        
        try:
            photo_id = query.message.photo[-1].file_id if query.message.photo else context.user_data.get('last_photo_id')
            news_url = query.message.caption.split('🔗 খবরের লিংক:\n')[-1].strip() if '🔗 খবরের লিংক:\n' in query.message.caption else ""
            title = query.message.caption.split('\n\n🔗')[0].replace('**', '').strip()

            file_obj = await context.bot.get_file(photo_id)
            post_caption = f"{title}\n\nসংবাদের বিস্তারিত পড়তে ক্লিক করুন:\n{news_url}\n\n#moktokontho #news #bangladesh"

            payload = {"photo_url": file_obj.file_path, "caption": post_caption}
            res = requests.post(MAKE_WEBHOOK_URL, json=payload, timeout=25)
            
            if res.status_code == 200:
                await query.message.reply_text("🎉 অভিনন্দন! লিংকসহ পোস্টটি সফলভাবে ফেসবুকে লাইভ হয়ে গেছে!")
            else:
                await query.message.reply_text(f"সমস্যা হয়েছে (Status: {res.status_code})")
        except Exception as err:
            await query.message.reply_text(f"সমস্যা হয়েছে: {str(err)}")

if __name__ == '__main__':
    request_config = HTTPXRequest(connect_timeout=60.0, read_timeout=60.0, write_timeout=60.0, pool_timeout=60.0)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).request(request_config).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(button_click))

    print("বট ক্লাউড সার্ভার মোডে চালু হয়েছে!")
    app.run_polling(drop_pending_updates=True)
