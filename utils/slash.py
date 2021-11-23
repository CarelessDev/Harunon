from discord_slash.utils.manage_commands import create_choice, SlashCommandOptionType as SOT


class SlashUtils:
    @staticmethod
    def ephemeral(text: str = "Reduce mess caused to channel"):
        return create_choice(
            name="ephemeral",
            description=text,
            required=False,
            option_type=SOT.BOOLEAN,
        )
