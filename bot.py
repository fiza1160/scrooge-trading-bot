import time
from app import create_app

bot = create_app()

while True:
    bot.introduce()
    time.sleep(30)
