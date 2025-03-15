import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.environ["TOKEN"]
usuarios_suscritos = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando para iniciar el bot y registrar el chat ID."""
    chat_id = update.effective_chat.id
    usuarios_suscritos[chat_id] = True

    await update.message.reply_text(
        f"¡Hola! Soy tu bot de buenos días. Te enviaré un saludo cada mañana a las 8:00.\n"
        f"Tu chat ID es: {chat_id}\n"
        f"Has sido suscrito a los mensajes de buenos días."
    )
    logging.info(f"Nuevo usuario suscrito con chat_id: {chat_id}")


async def buenos_dias(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía un mensaje de buenos días a todos los usuarios suscritos."""
    for chat_id in usuarios_suscritos.keys():
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text="¡Buenos días! Espero que tengas un día maravilloso. ☀️"
            )
            logging.info(f"Mensaje enviado a chat_id: {chat_id}")
        except Exception as e:
            logging.error(f"Error al enviar mensaje a {chat_id}: {e}")


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando para cancelar la suscripción."""
    chat_id = update.effective_chat.id
    if chat_id in usuarios_suscritos:
        del usuarios_suscritos[chat_id]
        await update.message.reply_text("Has cancelado la suscripción a los mensajes de buenos días.")
        logging.info(f"Usuario canceló suscripción: {chat_id}")
    else:
        await update.message.reply_text("No estabas suscrito a los mensajes de buenos días.")


def start_scheduler(application: Application) -> None:
    """Configura y arranca el programador."""
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        buenos_dias,
        "cron",
        hour=8,
        minute=0,
        args=[application.bot]
    )

    scheduler.start()
    logging.info("Scheduler iniciado correctamente.")


async def main_async():
    """Configura el bot y corre el programador asincrónicamente."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))

    start_scheduler(application)

    await application.initialize()

    logging.info("Iniciando el bot...")
    await application.start()

    logging.info("Bot corriendo. Presiona Ctrl+C para detenerlo.")
    await asyncio.Event().wait()


def main():
    """Punto de entrada principal del script."""
    try:
        loop = asyncio.get_event_loop()

        loop.run_until_complete(main_async())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot detenido manualmente.")
    except RuntimeError as e:
        logging.error(f"Error de tiempo de ejecución: {e}")


if __name__ == "__main__":
    main()