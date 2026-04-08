import os
import asyncio
import uuid
import shutil
import logging

# Sahi split: 'telegram' for data structures, 'telegram.ext' for logic
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    filters, 
    ContextTypes
)

# --- LOGGING ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- CONFIGURATION ---
TOKEN = 'YOUR_BOT_TOKEN_HERE' # <-- Apna token yahan daal
BASE_DOWNLOAD_PATH = "./spotyshell_temp"

# --- COMMAND FUNCTIONS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Apna actual Razorpay link yahan daalna
    #support_url = "https://rzp.io/l/your_actual_link"
    
    keyboard = [
        [
            InlineKeyboardButton("🎵 Enjoy Music", callback_data="enjoy_music"),
            InlineKeyboardButton("❤️ Support Me", url=support_url)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome to SpotyShell! 🚀\n\n"
        "Click the buttons below to start listening or support the project.",
        reply_markup=reply_markup
    )

async def enjoy_music_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Button ka spinner stop karne ke liye
    
    instructions = (
        "🎵 **How to use SpotyShell:**\n\n"
        "1. **Spotify Link:** Paste any Spotify track link to download.\n"
        "2. **YouTube Link:** Paste a YouTube video link for audio.\n"
        "3. **Search:** Simply type the song name (e.g., 'Starboy') to search.\n\n"
        "Ready to listen? Send me a link or a song name now!"
    )
    
    # Message edit karega taaki chat clean rahe
    await query.edit_message_text(text=instructions, parse_mode='Markdown')

async def download_worker(update: Update, chat_id: int, query: str):
    job_id = f"{chat_id}_{uuid.uuid4().hex[:6]}"
    user_dir = os.path.join(BASE_DOWNLOAD_PATH, job_id)
    os.makedirs(user_dir, exist_ok=True)
    
    status_msg = await update.message.reply_text("Analyzing Priority List...🔍")

    # Source Identification
    if "spotify.com" in query:
        method = "Spotify Metadata Extraction"
        cmd = ["spotdl", "download", query, "--output", user_dir, "--format", "mp3", "--bitrate", "320k"]
    elif "youtube.com" in query or "youtu.be" in query:
        method = "YouTube Direct Stream"
        cmd = ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0", "--embed-metadata", "--embed-thumbnail", "-o", f"{user_dir}/%(title)s.%(ext)s", query]
    else:
        method = "YT-Music Search (Top 1st Result)"
        cmd = ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0", "--embed-metadata", "--embed-thumbnail", "-o", f"{user_dir}/%(title)s.%(ext)s", f"ytsearch1:{query}"]

    await status_msg.edit_text(f"Priority: {method}\nProcessing audio stream...🚀")

    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    files = [f for f in os.listdir(user_dir) if f.endswith(".mp3")]
    
    if not files:
        await status_msg.edit_text("Priority Error ❌: Could not fetch result. Check link or query.")
        logging.error(f"Download Error: {stderr.decode()}")
    else:
        for file_name in files:
            file_path = os.path.join(user_dir, file_name)
            await status_msg.edit_text(f"📤 Delivering: {file_name}")
            try:
                with open(file_path, 'rb') as audio:
                    await update.message.reply_audio(
                        audio=audio, 
                        title=file_name.replace(".mp3", ""),
                        caption=f"{file_name} delivered ✅"
                    )
            except Exception as e:
                await update.message.reply_text(f"Error sending {file_name}: {str(e)}")
        
        await status_msg.delete()

    shutil.rmtree(user_dir)

async def handle_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    chat_id = update.message.chat_id
    asyncio.create_task(download_worker(update, chat_id, query))

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    if not os.path.exists(BASE_DOWNLOAD_PATH):
        os.makedirs(BASE_DOWNLOAD_PATH)
        
    app = Application.builder().token(TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(enjoy_music_callback, pattern='^enjoy_music$'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_request))
    
    print(">>> SpotyShell is live...")
    app.run_polling()
