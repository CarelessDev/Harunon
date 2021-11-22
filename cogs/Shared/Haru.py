import discord


class Haru():
    @staticmethod
    def get_emoji(ctx, emoji_name: str):
        return discord.utils.get(ctx.bot.emojis, name=emoji_name)
