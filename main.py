import Scraping
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler
from telegram.ext import filters


token = open('venv/settings.env','r').read()
print(token)

async def bot_reply(update: Update, ctx):
    user_input = update.message.text    #что написали боту
    reply = Scraping.read_from_csv()
    print(user_input)
    await update.message.reply_text(reply)


app = ApplicationBuilder().token(token).build()
handler = MessageHandler(filters.TEXT, bot_reply)
app.add_handler(handler)

app.run_polling()