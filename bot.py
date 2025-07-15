import yaml
import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# 預先載入 config，避免多次開啟檔案
with open("config.yml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
token = config["discord"]["token"]
guild_id = int(config["discord"]["guild_id"])

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="喵"))
    guild = discord.Object(id=guild_id)
    bot.tree.copy_global_to(guild=guild)
    slash = await bot.tree.sync(guild=guild)
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')
    print(f'Synced {len(slash)} commands.')
    for cmd in slash:
        print(f'Command: {cmd.name} - {cmd.description}')

    # for g in bot.guilds:
    #     print(f"Guild: {g.name} ({g.id})")
    #     for c in g.text_channels:
    #         print(f"  - #{c.name} ({c.id})")

@bot.command(name='help')
async def help_command(ctx):
    await ctx.send(
        "可用指令列表:\n"
        "!help - 顯示此幫助訊息\n"
        "/events - 顯示所有事件\n"
        "/add_event - 添加新事件\n"
    )

@bot.command()
async def load(ctx, extension):
    try:
        await bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"Loaded {extension} successfully")
    except Exception as e:
        await ctx.send(f"Failed to load {extension}: {e}")

@bot.command()
async def unload(ctx, extension):
    try:
        await bot.unload_extension(f"cogs.{extension}")
        await ctx.send(f"Unloaded {extension} successfully")
    except Exception as e:
        await ctx.send(f"Failed to unload {extension}: {e}")

@bot.command()
async def reload(ctx, extension):
    try:
        await bot.reload_extension(f"cogs.{extension}")
        await ctx.send(f"reload {extension} success")
    except Exception as e:
        await ctx.send(f"reload {extension} failed: {e}")

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(filename)

async def main():
    async with bot:
        await load_extensions()
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
