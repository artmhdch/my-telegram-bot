import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# ضع التوكن الخاص ببوتك هنا (الذي أخذته من BotFather)
TOKEN = "ضع_التوكن_الخاص_ببك_هنا"

# دالة الترحيب عند الضغط على /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك في بوت التحميل السريع! 🚀\n"
        "أرسل لي أي رابط فيديو من (تيك توك، فيسبوك، إنستغرام) وسأقوم بتحميله لك مجاناً وبدون علامة مائية."
    )

# دالة التعامل مع الروابط وتحميل الفيديو
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    # التأكد من أن المستخدم أرسل رابطاً فعلياً
    if not url.startswith(("http://", "https://")):
        await update.message.reply_text("الرجاء إرسال رابط صحيح يبدأ بـ http أو https.")
        return

    status_message = await update.message.reply_text("جاري معالجة الرابط وتحميل الفيديو... انتظر لحظة ⏳")

    # إعدادات أداة التحميل المجانية yt-dlp
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # اختيار أفضل جودة mp4
        'outtmpl': 'video_%(id)s.%(ext)s', # اسم الملف المؤقت
        'quiet': True,
    }

    try:
        # تشغيل عملية التحميل في بيئة منفصلة حتى لا يتوقف البوت
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # في بعض الأحيان قد تختلف اللاحقة بعد الدمج
            if not os.path.exists(filename):
                filename = filename.rsplit('.', 1)[0] + '.mp4'

        # إرسال الفيديو للمستخدم داخل تلغرام
        await status_message.edit_text("جاري رفع الفيديو إلى تلغرام... 📤")
        with open(filename, 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption="تم التحميل بنجاح عبر بوتك المجاني! 🎉")
        
        # مسح الملف من خادم الاستضافة حتى لا تمتلئ الذاكرة المجانية
        os.remove(filename)
        await status_message.delete()

    except Exception as e:
        print(f"Error: {e}")
        await status_message.edit_text("عذراً، حدث خطأ أثناء تحميل هذا الفيديو. تأكد من أن الحساب ليس خاصاً (Private).")
        if os.path.exists(filename):
            os.remove(filename)

# تشغيل البوت
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("البوت يعمل الآن بنجاح...")
    application.run_polling()

if __name__ == '__main__':
    main()
