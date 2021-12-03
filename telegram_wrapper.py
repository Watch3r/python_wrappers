import requests


class telegram():
    def send_message(self, message: str, token: str, chat_id: str):
        """
        Send a message to a Telegram channel using a bot.
        :param message: string: Message to send.
        :param token: string: Token of bot to use.
        :param chat_id: string: Chat ID of where message should be sent.
        :return: boolean: True if sent successfully, False if not.
        """
        s = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=Markdown&text={}'.format(token, chat_id, message)
        try:
            requests.get(s).json()
            return True
        except:
            return False


if __name__ == '__main__':
    pass
