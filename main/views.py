from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from main.bot import bot
import telebot, traceback

@csrf_exempt
def webhook(request: HttpRequest):
    try:
        update = telebot.types.Update.de_json(request.body.decode())
        if update:
            bot.process_new_updates([update])
        
        return HttpResponse('!')
    except Exception as e:
        traceback.print_exc()
    
    return HttpResponse('!', status = 500)