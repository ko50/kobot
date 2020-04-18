from re import match
import os
import discord
import asyncio
import datetime

class Kobot(discord.Client):
    def __init__(self, token, base_channel_id):
        super(Kobot, self).__init__()
        self.token = token
        self.base_channel_id = base_channel_id
        self.timer = {}
        self.timezone = 9

        self.base_channel = None

    def launch(self):
        self.run(self.token)

    async def count_time(self):
        while True:
            for user in self.timer:
                try:
                    if self.timer[user] != "pause":
                        print(self.timer[user])
                        self.timer[user] += 1
                except TypeError:
                    pass
            await asyncio.sleep(1)

    async def on_ready(self):
        self.base_channel = self.get_channel(self.base_channel_id)
        asyncio.ensure_future(self.count_time())
        print('Successfully Logged in')
        await self.base_channel.send("log in")


    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content == 'power':
            await message.channel.send('is power')
            return

        if message.content[0]=="!":
            #if message.content == '*timer start':
            await self.valid_command(message, message.author)
            return

    async def valid_command(self, message: discord.Message, user: discord.Client.user):
        """
        メッセージがコマンドとして入力された場合、実行される
        """
        user_order = message.content[1:].split()
        command = user_order[0]
        print(user_order)
        if command == "timer":
            if len(user_order) < 2:
                await message.channel.send("なにかがおかしい")
                return
            await self.personal_timer(user_order[1], message)
            return

    async def personal_timer(self, order_type: str, message: discord.Message):
        user = message.author
        channel = message.channel
        if not user in self.timer:
            self.timer[user] = "pause"
        user_time = self.timer[user]

        if order_type == "start":
            if user_time == "pause":
                self.timer[user] = 0
                await channel.send(user.mention + "\nタイマーをスタートしたよ")
            else:
                await channel.send("タイマーは既にスタートしているよ")
        elif order_type == "stop":
            if user_time == "panse":
                await channel.send("タイマーはスタートしていないよ")
            else:
                time = self.format_time(user_time)
                await channel.send(user.mention + "\nタイマーを止めたよ。\n経過時間は {} だよ".format(time))
                self.timer[user] = "pause"
        elif order_type == "preview":
            if user_time == "pause":
                await channel.send("タイマーはスタートしていないよ")
            else:
                time = self.format_time(user_time)
                await channel.send(user.mention + "\nタイマーの今時点での経過時間は {} だよ".format(time))
        else:
            await channel.send("なにかがおかしい")
        return

    def format_time(self, second):
        """
        クソコード定期
        """
        result = ""
        minute    = second//60
        second %= 60
        hour    = minute//60
        minute    %= 60
        for it in [hour, minute, second]:
            if it < 10:
                result += "0{}".format(it)
            else:
                result += str(it)
            result += " : "
        return result[:12]

if __name__ == "__main__":
    TOKEN = os.environ["KOBOT_TOKEN"]
    KOBOT = Kobot(TOKEN, base_channel_id=700920193580531712)
    KOBOT.launch()