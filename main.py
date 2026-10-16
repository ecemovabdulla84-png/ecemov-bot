import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8672293368:AAGz8MrkRD86jl1hzNBj31JbJZqHXtTPs3U"

# Render ucun kicik veb server (Xetanin qarsisini almaq ucun)
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# Bot funksiyalari
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salam! Videonu 'Document' (Sənəd) şəklində göndərin, 4K 120fps kimi emal edim.")

async def process_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc or not doc.mime_type.startswith("video/"):
        await update.message.reply_text("Xahiş edirəm videonu sənəd (Document) formatında göndərin.")
        return

    msg = await update.message.reply_text("Video qəbul edildi! Emal olunur...")
    
    file = await doc.get_file()
    input_path = "input_video.mp4"
    output_path = "output_4k.mp4"
    
    await file.download_to_drive(input_path)
    
    # FFmpeg komandasi
    cmd = f'ffmpeg -y -i "{input_path}" -vf "scale=3840:2160" -r 120 -c:v libx264 -crf 15 -preset fast "{output_path}"'
    
    proc = await asyncio.create_subprocess_shell(cmd)
    await proc.communicate()
    
    await msg.edit_text("Yüklənir...")
    with open(output_path, 'rb') as video_file:
        await update.message.reply_document(document=video_file, caption="4K 120FPS Hazırdır! 🔥")
        
    if os.path.exists(input_path): os.remove(input_path)
    if os.path.exists(output_path): os.remove(output_path)

if __name__ == '__main__':
    # Veb serveri arxa fonda basladırıq
    threading.Thread(target=run_http_server, daemon=True).start()
    
    # Telegram botu basladırıq
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, process_video))
    app.run_polling()
