import discord
from discord.ext import commands
from discord import app_commands
import api.notion_calendar as calendar
import api.error_handle as error
from datetime import datetime
import yaml

try:
    with open("config.yml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
except:
    config = [[]]
    config["discord"]["secret_channel"]
    config["discord"]

ALLOWED_CHANNELS = [
    int(config["discord"]["secret_channel"]),
    int(config["discord"]["general_channel"])
]

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.command(name="events", description="顯示所有事件")
    async def events(self, ctx: commands.Context):
        await ctx.send("顯示所有事件")

    @app_commands.command(name="events", description="顯示所有事件")
    @app_commands.describe(method="all, future, ...")
    async def events(self, interaction: discord.Interaction, method: str = "future"):
        
        if interaction.channel.id not in ALLOWED_CHANNELS:
            # await interaction.response.send_message(
            #     "This command can only be used in specific channels.",
            #     ephemeral=True
            # )
            return
        
        try:

            events = calendar.fetch_event("general")

            events = sorted(events, key=lambda e: (e['start'] is None, e['start']))

            if method == "future":
                events = [event for event in events if event['start'] is not None]
                events = [event for event in events if datetime.strptime(event['start'], "%Y-%m-%d").date() > discord.utils.utcnow().date()]


            if not events:
                await interaction.response.send_message("目前沒有任何事件。", ephemeral=True)
                return
            
            embed = discord.Embed(title="事件列表", color=discord.Color.blue())
            for event in events:
                embed.add_field(
                    name=event['name'],
                    value=f"開始時間: {event['start']}\n結束時間: {event['end']}\n負責人員: {', '.join(event['assigned']) if event['assigned'] else '無'}",
                    inline=False
                )
            print(f"Events: {events}")
            embed.set_footer(text=f"共 {len(events)} 個事件")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await error.handle_error(e, interaction)

        
async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))