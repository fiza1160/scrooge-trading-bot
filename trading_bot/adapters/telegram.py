import telebot


class AdapterTelegram:

    def __init__(self, token, chat_id):
        self._token = token
        self._chat_id = chat_id
        self._bot = telebot.TeleBot(self._token)

    async def notify(self, msg: str):
        self._bot.send_message(self._chat_id, msg)
