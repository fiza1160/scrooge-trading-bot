import telebot


class Notifier:

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.bot = telebot.TeleBot(self.token)

    async def notify(self, decision_queue):
        while True:
            message = await decision_queue.get()
            self.bot.send_message(self.chat_id, message)
            decision_queue.task_done()