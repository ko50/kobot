import os
import discord
import asyncio
import datetime
import json

INTRODUCTION = \
"```\
*timer subcommand :ユーザーごとに割り当てられるストップウオッチ\n\
    |-- start\n\
    |-- stop\n\
    |-- preview\n\
    |-- pause\n\
\n\
*status メンション :メンションしたユーザーの状態を表示\n\
\n\
```\n"

class Kobot(discord.Client):
    def __init__(self, token, base_channel_id, base_vc_id):
        super(Kobot, self).__init__()
        self.token = token
        self.base_channel_id = base_channel_id
        self.base_vc_id = base_vc_id
        self.timer = {}

        self.base_channel = None

    def launch(self):
        self.run(self.token)

    async def count_time(self):
        while True:
            for user, time in self.timer.items():
                if type(time) == int:
                    self.timer[user] += 1
                    print("{}: {}".format(user, time))
            await asyncio.sleep(1)

    async def on_ready(self):
        self.base_channel = self.get_channel(self.base_channel_id)
        self.base_vc = self.get_channel(self.base_vc_id)
        asyncio.ensure_future(self.count_time())
        print('Successfully Logged in')


    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content == 'power':
            await message.channel.send('is power')
            return

        if "とは" in message.content:
            message.content

        if ("!?" in message.content or "！？" in message.content) and len(self.base_vc.members)>=2:
            await self.play_bgm(message, "！？！？！？！？！？！？！！？！？", "assets/！？！？！？！？！？！？！！？！？.mp3")

        if ("??" in message.content or "？？" in message.content) and len(self.base_vc.members)>=2:
            await self.play_bgm(message, "？？？？？？？？？？？？？？？？？？", "assets/？？？？？？？？？？？？？？？？？？.mp3")

        if message.content[0]=="*":
            await self.valid_command(message, message.author)
            return

#        with open("kobot/assets/typo.json", encoding="utf-8") as t:
#            model_typo_list = json.load(t)["typo"]
#        for model_typo in model_typo_list:
#            if model_typo in message.content:
#                await message.channel.send("typoしましたね？カス")

    async def valid_command(self, message: discord.Message, user: discord.Client.user):
        """
        メッセージがコマンドとして入力された場合、実行される
        """
        user_order = message.content[1:].split()
        command     = user_order[0]
        other_order = user_order[1:]
        print("from:    {}\ncommand: {}".format(message.author, user_order))
        if command == "info":
            await message.channel.send(INTRODUCTION)
            return

        if command == "timer":
            if len(user_order) < 2:
                await message.channel.send(user.mention + "\n入力エラー")
                return
            await self.personal_timer(user_order[1], message)
            return

        if command == "status":
            if len(user_order) < 2 or user_order[1][1] != "@":
                await message.channel.send(user.mention + "\n入力エラー")
                return
            mentioned_user_id = user_order[1][3:-1]
            for guild_user in message.guild.members:
                if mentioned_user_id == str(guild_user.id):
                    await message.channel.send("ユーザーID: {} の状態は {} です".format(mentioned_user_id, guild_user.status))
                    return
            await message.channel.send(user.mention + "\nそんな人ここにはいないです")
            print(message.content)
            return

#        if command == "add":
#            if other_order[0] == "typo" and len(other_order) >= 2:
#                typo = " ".join(other_order[1:])
#                self.add_typo(typo)
#                await message.channel.send("typo {} をtypo listに追加".format(typo))

    async def personal_timer(self, order_type: str, message: discord.Message):
        """
        ユーザーごとにストップウォッチ式で時間計測できる
        """
        user = message.author
        channel = message.channel
        if not user in self.timer:
            self.timer[user] = "stop"
        user_time = self.timer[user]

        if order_type == "start":
            if user_time == "stop":
                self.timer[user] = 0
                await channel.send(user.mention + "\nタイマーをスタートしました")
            elif type(user_time) == int:
                await channel.send(user.mention + "\nタイマーは既にスタートしています")
            else:
                user_time = int(user_time[5:])
                self.timer[user] = user_time
                time = self.format_time(user_time)
                await channel.send(user.mention + "\nタイマーを経過時間 {} から再スタート".format(time))

        elif order_type == "stop":
            if user_time == "stop":
                await channel.send(user.mention + "\nタイマーは動いていません")
            elif type(user_time) == int:
                time = self.format_time(user_time)
                await channel.send(user.mention + "\nタイマーを停止しました。\n経過時間は {} ".format(time))
                self.timer[user] = "stop"
            else:
                user_time = int(user_time[5:])
                time = self.format_time(user_time)
                await channel.send(user.mention + "\nタイマーを停止しました。\n経過時間は {} ".format(time))
                self.timer[user] = "stop"

        elif order_type == "preview":
            if user_time == "stop":
                await channel.send(user.mention + "\nタイマーは動いてないため経過時間は0秒")
            elif type(user_time) == int:
                time = self.format_time(user_time)
                await channel.send(user.mention + "\nタイマーの現時点での経過時間は {} ".format(time))
            else:
                user_time = int(user_time[5:])
                time = self.format_time(user_time)
                await channel.send(user.mention + "\nタイマーは経過時間 {} で停止中".format(time))

        elif order_type == "pause":
            if type(user_time) == int:
                time = self.format_time(user_time)
                await channel.send(user.mention + "\nタイマーを経過時間 {} で一時停止".format(time))
                self.timer[user] = "pause" + str(user_time)
            else:
                await channel.send(user.mention + "\nタイマーは動いていません")

        else:
            await channel.send(user.mention + "\n入力エラー")
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

    async def play_bgm(self, message: discord.Message, with_message: str, source_path: str):
        await message.channel.send(with_message)
        vc_client = await self.base_vc.connect()
        if not vc_client:
            return
        audio_source = discord.FFmpegPCMAudio(source_path)
        vc_client.play(audio_source)
        await asyncio.sleep(11)
        await vc_client.disconnect(force=True)

    def add_typo(self, new_typo):
        with open("kobot/assets/typo.json", encoding="utf-8") as t:
            model_typo_list = json.load(t)["typo"]
            if new_typo in model_typo_list:
                return
        model_typo_list.append(new_typo)
        print(new_typo)
        print(model_typo_list)
        new_json = "{\"typo\": " + str(model_typo_list) + "}"
        with open("kobot/assets/typo.json", "w", encoding="utf-8") as t:
            t.write(new_json)

if __name__ == "__main__":
    TOKEN = os.environ["KOBOT_TOKEN"]
    KOBOT = Kobot(TOKEN, base_channel_id=701058219111612427, base_vc_id=683939861539192865)
    KOBOT.launch()