from django.conf import settings
from telebot import TeleBot, types
from PIL import Image
from io import BytesIO
import re, random, os

bot = TeleBot(settings.TELEGRAM_BOT_TOKEN)

bot.remove_webhook()
bot.set_webhook(settings.BASE_URL + '/supersecret/hooks/' + bot.token)

LIST_IMAGE = {}

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


@bot.message_handler(content_types = ['document'], func = lambda msg: msg.document.mime_type.startswith('image/'))
def add_photo_with_document(message):
    if not isinstance(LIST_IMAGE.get(message.from_user.id), list):
        bot.reply_to(message, "Send /pdf for initialization")
        return
    
    if len(LIST_IMAGE[message.from_user.id]) >= 20:
        bot.reply_to(message, "Maximal 20 images :(")
        return
        
    if (message.document.file_size > 500_000):
        bot.reply_to(message, "Too large :(")
        return

    file = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file.file_path)
    image = Image.open(BytesIO(downloaded_file))
    
    LIST_IMAGE[message.from_user.id].append(image)
    bot.reply_to(message, f"[{len(LIST_IMAGE[message.from_user.id])}] Success add image, send command /done if finish")

@bot.message_handler(content_types = ["photo"])
def add_photo(message):
	if not isinstance(LIST_IMAGE.get(message.from_user.id), list):
		bot.reply_to(message, "Send /pdf for initialization")
		return

	if len(LIST_IMAGE[message.from_user.id]) >= 20:
		bot.reply_to(message, "Maximal 20 images :(")
		return

	file = bot.get_file(message.photo[1].file_id)
	downloaded_file = bot.download_file(file.file_path)
	image = Image.open(BytesIO(downloaded_file))

	LIST_IMAGE[message.from_user.id].append(image)
	bot.reply_to(message, f"[{len(LIST_IMAGE[message.from_user.id])}] Success add image, send command /done if finish")

@bot.message_handler(commands = ["pdf"])
def pdf(message):
	bot.send_message(message.from_user.id, "Okay, now send your photos one by one")

	if not isinstance(LIST_IMAGE.get(message.from_user.id), list):
		LIST_IMAGE[message.from_user.id] = []

@bot.message_handler(commands = ["done"])
def done(message):
	images = LIST_IMAGE.get(message.from_user.id)

	if isinstance(images, list):
		del LIST_IMAGE[message.from_user.id]

	if not images:			
		bot.send_message(message.from_user.id, "No image !!")
		return

	path = str(random.randint(0, 100000)) + ".pdf"
	images[0].save(path, save_all = True, append_images = images[1:])
	bot.send_document(message.from_user.id, open(path, "rb"), caption = "Here your pdf !!")
	os.remove(path)