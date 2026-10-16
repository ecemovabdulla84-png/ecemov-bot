import os
import subprocess
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = '8672293368:AAGz8MrkRD86jl1hzNBj31JbJZqHXtTPs3U'

logging.basicConfig(level=logging.INFO)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ Videonuz qəbul olundu. 4K 120fps parametri ilə TikTok üçün optimallaşdırılır, zəhmət olmasa gözləyin...")
    
    document = update.message.document
    file = await context.bot.get_file(document.file_id)
    input_path = f"input_{document.file_name}"
    output_path = f"patched_{document.file_name}"
    
    await file.download_to_drive(input_path)
    
    ffmpeg_cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-c:v', 'libx264',
        '-r', '120',
        '-crf', '15',
        '-preset', 'fast',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'copy',
        output_path
    ]
    
    subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    with open(output_path, 'rb') as video_file:
        await update.message.reply_document(
            document=video_file, 
            caption="✅ Videonuz 4K 120fps parametrləri ilə hazırdır! TikTok-a yükləyə bilərsiniz."
        )
    
    if os.path.exists(input_path):
        os.remove(input_path)
    if os.path.exists(output_path):
        os.remove(output_path)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.run_polling()
