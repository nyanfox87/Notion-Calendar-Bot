import discord
from discord.ext import commands
from discord import app_commands
import yaml

ALLOWED_CHANNELS = [yaml.safe_load(open("config.yml", "r"))["discord"]["secret_channel"]] + [yaml.safe_load(open("config.yml", "r"))["discord"]["general_channel"]]


class TestCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx: commands.Context):
        if ctx.channel.id not in ALLOWED_CHANNELS:
            await ctx.send("This command can only be used in specific channels.")
            return
        await ctx.send("Test command executed!")

    @app_commands.command(name="test", description="A test command")
    @app_commands.describe(param="An optional parameter for testing")
    async def test_command(self, interaction: discord.Interaction, param: str = None):
        if interaction.channel.id not in ALLOWED_CHANNELS:
            await interaction.response.send_message(
                "This command can only be used in specific channels.",
                ephemeral=True
            )
            return
        try:
            await interaction.response.send_message(
                f"Received parameter: {param}" if param else "No parameter provided."
            )

            embed = discord.Embed(
                title="Test Embed",
                description="This is a test embed message.",
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed)

        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"An error occurred: {str(e)} Please contact the administrator.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"An error occurred: {str(e)} Please contact the administrator.",
                    ephemeral=True
                )



async def setup(bot: commands.Bot):
    await bot.add_cog(TestCog(bot))
