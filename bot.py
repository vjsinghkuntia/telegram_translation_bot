import os
import logging
import pytesseract
from PIL import Image

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from deep_translator import GoogleTranslator

# Windows Tesseract path (keep for local, ignore on Render)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 🔐 GET TOKEN FROM ENVIRONMENT VARIABLE
TOKEN = os.getenv("BOT_TOKEN")

# ⚠️ SAFETY CHECK
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables!")

logging.basicConfig(level=logging.INFO)


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 Send me an image with Hindi text.\n"
        "I will extract and translate it to English (FREE AI)."
    )


# Image handler
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()

    image_path = "image.jpg"
    await file.download_to_drive(image_path)

    try:
        # OCR (Hindi text extraction)
        text = pytesseract.image_to_string(Image.open(image_path), lang="hin")

        if not text.strip():
            await update.message.reply_text("❌ No text found in image.")
            return

        # Free translation
        translated = GoogleTranslator(source="auto", target="en").translate(text)

        await update.message.reply_text(
            f"📝 Hindi Text:\n{text}\n\n🌍 English Translation:\n{translated}"
        )

    except Exception as e:
        await update.message.reply_text(f"⚠ Error processing image: {str(e)}")


def main():
    print("BOT STARTED ✔")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

    print("🤖 BOT RUNNING...")
    app.run_polling()


if __name__ == "__main__":
    main()
