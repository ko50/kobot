import discord

STOPPING = "stopping"
COUNTING = "counting"
PAUSING  = "pausing"

class StopWatch:
    """
    ユーザーと関連付けられたストップウォッチを管理するクラス

    ### Patamater
    - user_id  = そのストップウォッチを所有するユーザーのid
    - state = ストップウォッチの状態 (STOPING:停止中 COUNTING:計測中 PAUSING:一時停止中)
    - count = ストップウォッチの現在の秒数
    """
    def __init__(self, user_id: id):
        self.user_id  = user_id
        self.state = STOPPING
        self.count = 0
        self.mention = "<@!{}>\n".format(self.user_id)

    def increment(self):
        if self.state == COUNTING:
            self.count += 1

    async def start(self, channel):
        """
        時間計測を開始
        """
        time = format_time(self.count)

        if self.state == COUNTING:
            message = "既に計測中です。"
        elif self.state == PAUSING:
            message = "一時停止を解除。\n経過時間 {} から計測を再開しました。".format(time)
        elif self.state == STOPPING:
            message = "計測を開始しました。"
            self.count = 0

        await channel.send(self.mention + message)
        self.state = COUNTING

    async def stop(self, channel):
        """
        時間計測を停止
        """
        time = format_time(self.count)

        if self.state == COUNTING:
            message = "計測を停止しました。\n経過時間は {} でした。".format(time)
            self.count = 0
        elif self.state == PAUSING:
            message = "一時停止を解除しストップウォッチを停止しました。\n経過時間は {} でした。".format(time)
        elif self.state == STOPPING:
            message = "既に停止中です。"

        await channel.send(self.mention + message)
        self.state = STOPPING
        print(self.state)

    async def pause(self, channel):
        """
        時間計測を一時停止
        """
        time = format_time(self.count)

        if self.state == COUNTING:
            message = "計測を一時停止しました。\n現時点での経過時間は {} です。".format(time)
        elif self.state == PAUSING:
            message = "既に一時停止しています。"
        elif self.state == STOPPING:
            message = "計測は停止中です。"

        await channel.send(self.mention + message)
        self.state = PAUSING

    async def preview(self, channel):
        """
        現在の経過時間を表示
        """
        time = format_time(self.count)
        print(self.count)

        if self.state == COUNTING:
            message = "現在は時間を計測中\n経過時間は {} です。".format(time)
        elif self.state == PAUSING:
            message = "現在は一時停止中\n経過時間は {} です。".format(time)
        elif self.state == STOPPING:
            message = "現在は時間を計測していません。"

        await channel.send(self.mention + message)

    async def call_stop_watch(self, order: str, channel: discord.Message.channel):
        """
        a
        """

        if order == "start":
            await self.start(channel)

        elif order == "pause":
            await self.pause(channel)

        elif order == "stop":
            await self.stop(channel)

        elif order == "preview":
            await self.preview(channel)

        else:
            await channel.send("<@!{}>\n入力エラーです。\nデバッグ界の灰コーダー。".format(self.user_id))

        print(self.state)

def format_time(second):
    """
    秒数を受け取りhh:mm:ssの形のstringにして返す

    ここはU結界密度が高すぎてリファクタできない
    だれかリリンがリファクタできるくらいまで下げて
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

