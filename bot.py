import os
import asyncio
import uuid
import shutil
import logging
from telegram import Update
from telegram.ext import InlineKeyboardMarkup, InlineKeyboardButton, Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- LOGGING ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- CONFIGURATION ---
TOKEN = 'DO_NOT_SHARE_TOKEN'
BASE_DOWNLOAD_PATH = "./spotyshell_temp"

# --- Place this with your other command functions ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Use your actual Razorpay link here
    support_url = "https://rzp.io/l/your_link"
    
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

async def download_worker(update: Update, chat_id: int, query: str):
    # 1. Unique Workspace setup (Concurrency check)
    job_id = f"{chat_id}_{uuid.uuid4().hex[:6]}"
    user_dir = os.path.join(BASE_DOWNLOAD_PATH, job_id)
    os.makedirs(user_dir, exist_ok=True)
    
    status_msg = await update.message.reply_text("Analyzing Priority List...🔍")

    # 2. Source Identification & Priority Routing
    # Priority 1: Spotify (Metadata focus)
    if "spotify.com" in query:
        method = "Spotify Metadata Extraction"
        # Spotdl is great for metadata embedding
        cmd = ["spotdl", "download", query, "--output", user_dir, "--format", "mp3", "--bitrate", "320k"]
    
    # Priority 2: YouTube Direct Link
    elif "youtube.com" in query or "youtu.be" in query:
        method = "YouTube Direct Stream"
        cmd = [
            "yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0",
            "--embed-metadata", "--embed-thumbnail", 
            "-o", f"{user_dir}/%(title)s.%(ext)s", query
        ]
    
    # Priority 3: Search Query (YouTube Music 1st Result)
    else:
        method = "YT-Music Search (Top 1st Result)"
        # 'ytsearch1' ensures we pick the first match only
        cmd = [
            "yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0",
            "--embed-metadata", "--embed-thumbnail",
            "-o", f"{user_dir}/%(title)s.%(ext)s", f"ytsearch1:{query}"
        ]

    await status_msg.edit_text(f"Priority: {method}\nProcessing audio stream...🚀")

    # 3. Execution (Async Subprocess)
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    # 4. Delivery & Metadata Check
    # Check for both mp3 (spotdl/yt-dlp default)
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

    # 5. Cleanup Workspace
    shutil.rmtree(user_dir)

async def handle_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    chat_id = update.message.chat_id
    # Create background task so other users aren't blocked
    asyncio.create_task(download_worker(update, chat_id, query))

if __name__ == '__main__':
    if not os.path.exists(BASE_DOWNLOAD_PATH):
        os.makedirs(BASE_DOWNLOAD_PATH)
        
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_request))
    
    print(">>> SpotyShell is live...")
    app.run_polling()
# --- Inside your main() function or where handlers are added ---
application.add_handler(CommandHandler("start", start))
