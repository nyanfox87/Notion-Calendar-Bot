import discord
from discord.ext import commands, tasks
from discord import app_commands
import yaml
import api.error_handle as error
from datetime import datetime
from api.notion_calendar import fetch_event
import asyncio
import pytz

# 一次性讀取 config.yml 並轉型為 int
with open("config.yml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

ALLOWED_CHANNELS = [
    int(config["discord"]["secret_channel"]),
    int(config["discord"]["general_channel"])
]

class Notification(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_events.start()  # 啟動循環任務
        self.last_notificate_data = None

    async def send_notification(self, channel: discord.TextChannel, event: dict):
        if channel.id not in ALLOWED_CHANNELS:
            return

        try:
            print(f"Sending event {event['name']}")
            embed = discord.Embed(
                title=f"{event['name']}\n",
                description=(f"地點：{event.get('location', '無')}\n"
                             f"開始時間：{event.get('start', '無')}\n"
                             f"結束時間：{event.get('end', '無')}"),
                color=discord.Color.green()
            )
            await channel.send(embed=embed)
        except Exception as e:
            print(f"發送通知時發生錯誤：{str(e)}")
            await error.handle_error(e, None)

    @tasks.loop(seconds=10)
    async def check_events(self):
        tz = pytz.timezone('Asia/Taipei')
        now = datetime.now(tz)
        print(f"Checking events at {now}")

        if now.hour == 10 and now.minute <= 10:
            today_str = now.strftime('%Y-%m-%d')
            if self.last_notificate_data == today_str:
                print("Today finished")
                return
            else:
                self.last_notificate_data = today_str
        else:
            print("Not the time")
            return

        try:
            events = fetch_event("secret")
            tz = pytz.timezone('Asia/Taipei')
            current_time = datetime.now(tz)
            secret_channel_id = int(config["discord"]["secret_channel"])
            channel = await self.bot.fetch_channel(secret_channel_id)

            for event in events:
                try:
                    start_raw = event.get('start')
                    if not start_raw:
                        continue

                    try:
                        event_start = datetime.fromisoformat(start_raw).astimezone()
                    except ValueError:
                        print(f"無效的時間格式：{start_raw}")
                        continue

                    if event_start.date() == current_time.date():
                        await self.send_notification(channel, event)
                except Exception as e:
                    print(f"處理事件時發生錯誤：{e}")
                    continue

        except Exception as e:
            print(f"Error checking events at secret channel: {e}")
            await error.handle_error(e, None)
        
        print("Secret events finished")

        try:
            events = fetch_event("general")
            tz = pytz.timezone('Asia/Taipei')
            current_time = datetime.now(tz)
            general_channel_id = int(config["discord"]["general_channel"])
            channel = await self.bot.fetch_channel(general_channel_id)

            for event in events:
                try:
                    start_raw = event.get('start')
                    if not start_raw:
                        continue

                    try:
                        event_start = datetime.fromisoformat(start_raw).astimezone()
                    except ValueError:
                        print(f"無效的時間格式：{start_raw}")
                        continue

                    if event_start.date() == current_time.date():
                        await self.send_notification(channel, event)
                except Exception as e:
                    print(f"處理事件時發生錯誤：{e}")
                    continue
        except Exception as e:
            print(f"Error checking events at general channel: {e}")
            await error.handle_error(e, None)
        
        print("General events finished")

    @app_commands.command(name="test_notification", description="測試通知功能")
    async def test_notification(self, interaction: discord.Interaction):
        try:
            if interaction.channel.id not in ALLOWED_CHANNELS:
                await interaction.response.send_message("這個頻道不允許使用此指令", ephemeral=True)
                return
            
            ## maybe can detect current channel to send specific events

            events = fetch_event("general")
            if not events:
                await interaction.response.send_message("目前沒有事件可測試。", ephemeral=True)
                return

            # 先立即回應，避免 interaction 過期
            await interaction.response.send_message("正在發送測試通知...", ephemeral=True)

            count = 0
            for event in events:
                start_raw = event.get('start')
                if not start_raw:
                    continue
                await self.send_notification(interaction.channel, event)
                count += 1

            print(f"test_notification 發送完畢，共 {count} 筆。")

        except Exception as e:
            print(f"Error in test_notification: {e}")
            if interaction:
                await error.handle_error(e, interaction)
            else:
                await error.handle_error(e, None)


async def setup(bot: commands.Bot):
    await bot.add_cog(Notification(bot))
