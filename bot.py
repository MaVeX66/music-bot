import telebot
import requests
import os
from flask import Flask
import threading

# ⚠️ ВСТАВЬ СВОЙ ТОКЕН СЮДА
TOKEN = '9075692967:AAGXFoHqL8AN3gMzXTfGMhnDT_rnMHSnMSY'
bot = telebot.TeleBot(TOKEN)

AUDD_API_TOKEN = 'test' 

# Создаем веб-сервер (нужен для Render)
app = Flask('')

@app.route('/')
def home():
    return "Бот работает 24/7!"

def run_flask():
    # Render выдает порт в переменной окружения PORT
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! 🎵 Кидай мне голосовое сообщение (или аудио), и я попробую угадать песню!")

@bot.message_handler(content_types=['voice', 'audio'])
def handle_voice(message):
    bot.reply_to(message, "Слушаю... 🎧 Дай мне пару секунд.")
    
    try:
        file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open("temp_audio.ogg", 'wb') as new_file:
            new_file.write(downloaded_file)
            
        url = "https://api.audd.io/"
        files = {'file': open("temp_audio.ogg", 'rb')}
        data = {'api_token': AUDD_API_TOKEN, 'return': 'apple_music,spotify'}
        
        response = requests.post(url, files=files, data=data)
        result = response.json()
        
        if result.get('status') == 'success' and result.get('result'):
            song = result['result']
            artist = song['artist']
            title = song['title']
            
            text = f"🎶 Нашел!\n\n🎤 Исполнитель: {artist}\n🎵 Трек: {title}"
            
            if 'spotify' in song and song['spotify']:
                text += f"\n\n▶️ [Слушать в Spotify]({song['spotify']['external_urls']['spotify']})"
            if 'apple_music' in song and song['apple_music']:
                text += f"\n🍎 [Слушать в Apple Music]({song['apple_music']['url']})"
                
            bot.reply_to(message, text, disable_web_page_preview=True)
        else:
            bot.reply_to(message, "Не смог распознать. Попробуй напеть погромче или пришли кусок песни подольше. 😔")
            
        os.remove("temp_audio.ogg")
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")
        print(f"Ошибка: {e}")

if __name__ == '__main__':
    # Запускаем Flask в фоне
    t = threading.Thread(target=run_flask)
    t.start()
    # Запускаем бота
    print("Бот-мелодия запущен...")
    bot.polling(non_stop=True)
