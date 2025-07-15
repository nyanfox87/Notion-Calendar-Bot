import discord


async def handle_error(error: Exception, interaction: discord.Interaction = None):
    if not interaction.response.is_done():
        await interaction.response.send_message(
            f"發生錯誤：{str(error)} 請聯絡管理員",
            ephemeral=True
        )
    else:
        await interaction.followup.send(
            f"發生錯誤：{str(error)} 請聯絡管理員",
            ephemeral=True
        )