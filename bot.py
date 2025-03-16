import logging
import os
from datetime import datetime, time as datetime_time

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN_TELEGRAM = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_schedule_time():
    hour_str = os.environ.get('HOUR', '8')
    minute_str = os.environ.get('MINUTE', '0')

    try:
        hour = int(hour_str)
        minute = int(minute_str)
        return datetime_time(hour, minute)
    except ValueError:
        logging.warning("Invalid format for schedule time. Using default values.")
        return datetime_time(8, 0, 0)

SCHEDULED_TIME = get_schedule_time()

def get_time_diference(time1, time2):
    return (time2.hour - time1.hour) * 60 + (time2.minute - time1.minute)

def is_time_to_send():
    now = datetime.now().time()

    if now.hour == SCHEDULED_TIME.hour and now.minute == SCHEDULED_TIME.minute:
        return True

    if now > SCHEDULED_TIME:
        diff_minutes = get_time_diference(SCHEDULED_TIME, now)
        return diff_minutes < 10

    return False


async def check_and_send_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Verificando si es hora de enviar el mensaje...")
    now = datetime.now()

    if is_time_to_send():
        logging.info("Es hora de enviar el mensaje de buenos días!")
        try:
            await context.bot.send_message(chat_id=CHAT_ID, text='¡Buenos días! 🌞')
            logging.info("Mensaje enviado exitosamente!")
        except Exception as e:
            logging.error(f"Error al enviar el mensaje: {e}")
    elif (now.time() > SCHEDULED_TIME and
          get_time_diference(SCHEDULED_TIME, now.time()) < 10):
        logging.info("Han pasado menos de 10 minutos desde la hora programada.")
        try:
            await context.bot.send_message(chat_id=CHAT_ID, text='¡Buenos días! 🌞')
            logging.info("Mensaje enviado exitosamente!")
        except Exception as e:
            logging.error(f"Error al enviar el mensaje: {e}")
    else:
        logging.info("No es hora de enviar el mensaje aún.")



async def force_send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text='Enviando mensaje de prueba al chat configurado...')

    try:
        await context.bot.send_message(chat_id=CHAT_ID, text='¡Este es un mensaje de prueba forzado! 🧪')
        await update.message.reply_text(f'Mensaje enviado exitosamente al chat ID: {CHAT_ID}')
    except Exception as e:
        await update.message.reply_text(f'Error al enviar el mensaje: {e}')


async def get_current_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    await update.message.reply_text(f'El ID de este chat es: {chat_id}')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(f'¡Hola {user.first_name}! Soy tu bot de buenos días.')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Comandos disponibles:\n'
        '/start - Iniciar el bot\n'
        '/help - Ver ayuda\n'
        '/get_chat_id - Ver ID del chat actual\n'
        '/force_message - Enviar mensaje de prueba\n'
        'El bot enviará automáticamente buenos días a las 8:00 AM'
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Dijiste: {update.message.text}')


def main() -> None:
    app = Application.builder().token(TOKEN_TELEGRAM).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('get_chat_id', get_current_chat_id))
    app.add_handler(CommandHandler('force_message', force_send_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.job_queue.run_repeating(check_and_send_message, interval=300, first=10)

    logging.info('Bot iniciado y en funcionamiento...')
    app.run_polling()


if __name__ == '__main__':
    main()