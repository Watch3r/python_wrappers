import requests

class telegram():
    def send_message(self, message: str, token: str, chat_id: str):
        s = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=Markdown&text={}'.format(token, chat_id, message)
        return requests.get(s).json()

def main():
    pass

if __name__ == '__main__':
    main()