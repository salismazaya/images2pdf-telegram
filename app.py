from telebot import TeleBot, types
from flask import Flask, request
from io import BytesIO
from PIL import Image
import os, re, random

TOKEN = os.environ.get("TOKEN", "")
URL_WEBHOOK = os.environ.get("URL", "https://mbasic.facebook.com")
if not URL_WEBHOOK.endswith("/"):
	URL_WEBHOOK += "/"

bot = TeleBot(TOKEN)
server = Flask(__name__)

list_image = {}

@bot.message_handler(commands = ["start"])
def start(message):
	name = re.sub(r"[*_`]", "", message.from_user.first_name)
	msg = f"""
Hi _{name}_! this bot can convert your images to pdf

*[BOT COMMAND]*
/start _for start bot_
/pdf _for start convert_
/done _for finish convert_

Made with love by @salismiftah
		"""

	markup = types.InlineKeyboardMarkup()
	markup.add(types.InlineKeyboardButton("Source code this bot", url = "https://github.com/salismazaya/images2pdf-telegram"))
	bot.send_message(message.from_user.id, msg, reply_markup = markup, parse_mode = "Markdown")

@bot.message_handler(content_types = ["photo"])
def add_photo(message):
	if not isinstance(list_image.get(message.from_user.id), list):
		bot.reply_to(message, "Send /pdf for initialization")
		return

	if len(list_image[message.from_user.id]) >= 20:
		bot.reply_to(message, "Maximal 20 images :(")
		return

	file = bot.get_file(message.photo[1].file_id)
	downloaded_file = bot.download_file(file.file_path)
	image = Image.open(BytesIO(downloaded_file))

	list_image[message.from_user.id].append(image)
	bot.reply_to(message, f"[{len(list_image[message.from_user.id])}] Success add image, send command /done if finish")

@bot.message_handler(commands = ["pdf"])
def pdf(message):
	bot.send_message(message.from_user.id, "Okay, now send your photos one by one")

	if not isinstance(list_image.get(message.from_user.id), list):
		list_image[message.from_user.id] = []

@bot.message_handler(commands = ["done"])
def done(message):
	images = list_image.get(message.from_user.id)

	if isinstance(images, list):
		del list_image[message.from_user.id]

	if not images:			
		bot.send_message(message.from_user.id, "No image !!")
		return

	path = str(random.randint(0, 100000)) + ".pdf"
	images[0].save(path, save_all = True, append_images = images[1:])
	bot.send_document(message.from_user.id, open(path, "rb"), caption = "Here your pdf !!")
	os.remove(path)

@server.route("/" + TOKEN, methods = ["POST"])
def getMessage():
    json_string = request.get_data().decode()
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!"

@server.route("/")
def webhook():
	bot.remove_webhook()
	bot.set_webhook(URL_WEBHOOK + TOKEN)
	return "!"

if __name__ == "__main__":
	server.run(debug = True)