from telebot import TeleBot, types
from io import BytesIO
from PIL import Image
import os, re

TOKEN = "<api_token>"
bot = TeleBot(TOKEN)

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
	markup.add(types.InlineKeyboardButton("Source code this bot", url = "https://github.com/salismazaya/image2pdf-telegram"))
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

	path = str(message.from_user.id) + ".pdf"
	images[0].save(path, save_all = True, append_images = images[1:])
	bot.send_document(message.from_user.id, open(path, "rb"), caption = "Here your pdf !!")
	os.remove(path)

bot.polling()
