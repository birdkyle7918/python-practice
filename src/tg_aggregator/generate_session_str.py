from telethon.sessions import StringSession
from telethon.sync import TelegramClient

from settings import settings



if __name__ == "__main__":
    with TelegramClient(StringSession(), settings.API_ID, settings.API_HASH) as client:
        # 运行后，会在终端打印出一长串加密的字符串
        # 这就是你的 Session String，请务必保管好！
        print("你的 Session String 是:")