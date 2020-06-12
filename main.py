import os
import asyncio
import datetime
import json
import discord

from stop_watch import StopWatch

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

        self.stop_watch_list = []

    def launch(self):
        self.run(self.token)

    async def increase_stop_watch_count(self):
        while True:
            if self.stop_watch_list:
                for i in range(len(self.stop_watch_list)):
                    self.stop_watch_list[i].increment()
            await asyncio.sleep(1)

    async def on_ready(self):
        self.base_channel = self.get_channel(self.base_channel_id)
        self.base_vc = self.get_channel(self.base_vc_id)
        asyncio.ensure_future(self.increase_stop_watch_count())
        print('Successfully Logged in')


    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content == 'power':
            await message.channel.send('is power')
            return

        if "とは" in message.content:
            pass # TODO 実装

        if ("!?" in message.content or "！？" in message.content) and len(self.base_vc.members)>=2: # 収容
            await self.play_bgm(message, "！？！？！？！？！？！？！！？！？", "assets/！？！？！？！？！？！？！！？！？！.mp3") 
        if ("??" in message.content or "？？" in message.content) and len(self.base_vc.members)>=2:
            await self.play_bgm(message, "？？？？？？？？？？？？？？？？？？", "assets/？？？？？？？？？？？？？？？？？？.mp3")

        if message.content.startswith("*"):
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
                await message.channel.send("<@!{}>\n入力エラー".format(message.author.id))
                return

            index = -1

            for i in range(len(self.stop_watch_list)):
                sw = self.stop_watch_list[i]
                if message.author.id == sw.user_id:
                    index = i
                    break
            if index == -1:
                self.stop_watch_list.append(StopWatch(message.author.id))
                index = len(self.stop_watch_list) - 1

            await self.stop_watch_list[index].call_stop_watch(user_order[1], message.channel)
            return

# TODO
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

    async def play_bgm(self, message: discord.Message, with_message: str, source_path: str):
        await message.channel.send(with_message)
        vc_client = await self.base_vc.connect()
        if not vc_client:
            return

        # audio_source = discord.FFmpegPCMAudio(source_path)
        # vc_client.play(audio_source)
        await asyncio.sleep(11) # 曲の長さから取ったほうがいいですよね ハードコーディングやめろ
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