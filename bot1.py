import os
import re
import unicodedata
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your original card extraction logic - unchanged
def extract_card_data(text):
    """
    Extracts specific card data sequences from a block of text.
    The target format is: PAN|MM|YY|CVV
    """
    pattern = r'(\d{13,16}\|\d{2}\|\d{2,4}\|\d{3,4})'
    
    result = []
    for line in text.split('\n'):
        sanitized_line = re.sub(r'^[^\d]+', '', unicodedata.normalize("NFKC", line))
        match = re.search(pattern, sanitized_line)
        if match:
            result.append(match.group(1))
            
    return result

# This function runs when a user sends the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}!\n\n"
        "Send me any text, and I will extract card information for you.\n"
        "I'm looking for data in the format: `PAN|MM|YY|CVV`",
    )

# This function runs when a user sends any text message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles non-command text messages and extracts card data."""
    text = update.message.text
    filtered_values = extract_card_data(text)
    
    if filtered_values:
        response = "\n".join(filtered_values)
        await update.message.reply_text(f"Found matches:\n\n{response}")
    else:
        await update.message.reply_text("No matches found. Please check your input formatting.")

# --- THIS IS THE CHANGED PART ---
def main() -> None:
    """Start the bot using polling."""
    # Get the token from an environment variable for security
    token = os.environ.get("BOT_TOKEN")

    if not token:
        logger.error("BOT_TOKEN environment variable not set!")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    # We use 'polling' to continuously get updates from Telegram
    application.run_polling()

if __name__ == "__main__":
    main()
