import time


class App:
    def __init__(self, text: str, timer: int):
        self.text = text
        self.timer = timer

    def run(self):
        while True:
            print(self.text)
            time.sleep(self.timer)
