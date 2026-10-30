import os
import io
import time
import base64
import datetime
import requests
import subprocess
import edge_tts
import imageio_ffmpeg
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
hti_card = Html2Image(output_path=html = """<!DOCTYPE html><html><head><meta charset="utf-8">
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
return os.path.join(BASE_DIR, fname)html = """<!DOCTYPE html><html><head><meta charset="utf-8">
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
    box-shadow: 0 0 30px rgba(211,47,47,0.7);
    letter-spacing: 2px;
  }
  .card {
    width: 1000px; background: #000; border-radius: 28px; overflow: hidden;
    border: 3px solid rgba(255,255,255,0.2);
    box-shadow: 0 20px 60px rgba(0,0,0,0.9);
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
    border: 1px solid rgba(255,255,255,0.15);
  }
  .tag b { color: #ffcc00; }
</style></head><body>
  <div class="html = html.replace("__IMG__", img_src).replace("__TITLE__", title).replace("__SITE__", WEBSITE_NAME)
fname = f"reel_frame_{int(time.time())}.jpg"
hti_reel.screenshot(html_str=html, save_as=fname)
return os.path.join(BASE_DIR, fname)# মোশন ফিল্টার: স্থির ছবি থাকবে না, ধীরে ধীরে সিনেমাটিক জুম (Ken Burns Motion) হবে
video_filter = (
    "scale=1080:1920,"
    "zoompan=z='min(zoom+0.0008,1.08)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=25,"
    "drawbox=y=ih-14:color=red:width=iw:height=14:t=fill"  # লাইভ রেড প্রোগ্রেস বার
)

if has_bgm:cmd = [
        ffmpeg, "-y",
        "-loop", "1", "-i", frame_path,
        "-i", audio_path,
        "-stream_loop", "-1", "-i", BGM_PATH,
        "-filter_complex",
        f"[0:v]{video_filter}[v];"
        "[1:a]volume=1.4[voice];"
        "[2:a]volume=0.18[bgm];"
        "[voice][bgm]amix=inputs=2:duration=flags = 0x08000000 if os.name == 'nt' else 0
subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags)
return out_pathstatus = await update.message.reply_text("🔗 খবরটি পড়া হচ্ছে...")
try:
    title, img_url = scrape_news(url)
    
    # ফটোকার্ড তৈরি ও পাঠানো
    card_file = create_card(img_url, title)
    keyboard = [[InlineKeyboardButton("📘 ফেসবুকে পোস্ট করুন", callback_data="post_fb")]]
    
    caption_text = f"**{title}**\n\n🔗 খবরের লিংক:\n{url}"
    with open(card_file, 'rb') as photo:
        msg = await update.message.reply_photo(photo=photo, caption=caption_text, reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data['last_photo_id'] = msg.photo[-1].file_id

    # মোশন অ্যানিমেশন ও সাউন্ডসহ রিলস তৈরি
    try:
        await status.edit_text("🎬 সিনেমাটিক মোশন ও সাউন্ড ইফেক্টসহ রিলস তৈরি হচ্ছে...")
        audio_file = os.path.join(BASE_DIR, f"v_{int(time.time())}.mp3")
        await make_voice(title, audio_file)

        frame_file = create_reel_frame(img_url, title)
        video_file = os.path.join(BASE_DIR, f"reel_{int(time.time())}.mp4")
        make_cinematic_reel(frame_file, audio_file, video_file)

        with open(video_file, 'rb') as vid:
            await update.message.reply_video(
                video=vid,
                caption=f"🎬 **{title}**\n\n(মোশন অ্যানিমেশন ও টিভি সাউন্ডসহ সম্পূর্ণ রেডি!)",
                supports_streaming=True
            )
    except Exception as v_err:
        print("Video error:", v_err)

    await status.delete()

except Exception as e:
    await update.message.reply_text(f"সমস্যা হয়েছে: {str(e)}")if query.data == "post_fb":
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
        await query.message.reply_text(f"সমস্যা হয়েছে: {str(err)}")print("--------------------------------------------------")
print("বট সিনেমাটিক অ্যানিমেশন ও সাউন্ডসহ লাইভ হয়েছে!")
print("--------------------------------------------------")
app.run_polling(drop_pending_updates=True)---
