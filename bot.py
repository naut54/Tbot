import logging
import os
import time

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN_TELEGRAM = os.environ['TOKEN']

CHAT_ID = os.environ['CHAT_ID']

async def send_good_morning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=CHAT_ID, text='Good morning!')

async def save_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat.id
    await context.bot.send_message(chat_id=chat, text='Chat ID saved!')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(f'Hi {user.first_name}')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('You can start using me with: \n /start - To start the bot\n /help - To get help and more info')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'You said: {update.message.text}')

def schedule_tasks(app):
    job_queue = app.job_queue
    job_queue.run_repeating(send_good_morning, time=time.strptime("18:00:00", "%H:%M:%S"))

def main() -> None:
    app = Application.builder().token(TOKEN_TELEGRAM).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('save_chat_id', save_chat_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    schedule_tasks(app)

    logging.info('Bot is running...')
    app.run_polling()

if __name__ == '__main__':
    main()