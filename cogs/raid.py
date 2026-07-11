import re
import time
import psutil
import os
import discord
from discord import app_commands
from discord.ext import commands

from core.utils.helpers import (
    log_command,
    ZNE_INVITE, # Import ZNE_INVITE from helpers
)

from core.views import (
    SpamButton,
    PingPanel, 
    ThugView, 
    make_farm_panel, 
    make_custom_spam_panel, 
    make_filespam_panel, 
    FakeNitroView, 
    PresetManagementView
    )

from core.utils.db import get_user_presets, get_preset_by_title


class RaidCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def preset_autocomplete(self, interaction: discord.Interaction, current: str):
        presets = await get_user_presets(str(interaction.user.id))
        return [
            app_commands.Choice(name=p['title'], value=p['title'])
            for p in presets if current.lower() in p['title'].lower()
        ][:25]

    @app_commands.command(name="ra1d", description="[deprecated] self explanatory.")
    @app_commands.describe(preset="Optional preset to use for the raid")
    @app_commands.autocomplete(preset=preset_autocomplete)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ra1d(self, interaction: discord.Interaction, preset: str = None):
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        preset_content = None
        if preset:
            preset_content = await get_preset_by_title(str(interaction.user.id), preset)

        await interaction.followup.send(view=SpamButton(interaction.user.id, preset_content), ephemeral=True)
        await log_command(interaction, "ra1d", "user raided a server")

    @app_commands.command(name="interaction-ra1d", description="interaction raiding.")
    @app_commands.describe(preset="Optional preset to use for the interaction raid")
    @app_commands.autocomplete(preset=preset_autocomplete)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def interaction_ra1d(self, interaction: discord.Interaction, preset: str = None):
        await interaction.response.defer(ephemeral=True, thinking=True)

        preset_content = None
        if preset:
            preset_content = await get_preset_by_title(str(interaction.user.id), preset)

        await interaction.followup.send(
            view=make_farm_panel(interaction.user.id, 0, preset_content),
            ephemeral=True
        )
        await log_command(interaction, "interaction-ra1d", "user opened interaction farm panel")

    @app_commands.command(name="setpresetmsg", description="open the custom ra1d message panel")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def custom_ra1d(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await interaction.followup.send(view=PresetManagementView(interaction.user.id), ephemeral=True)
        await log_command(interaction, "custom_ra1d", "user opened custom message panel")

    @app_commands.command(name="thug", description="thug the server!!")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def thug(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await interaction.followup.send(view=ThugView(interaction.user.id), ephemeral=True)
        await log_command(interaction, "thug", "user thugged a server 😂")

    @app_commands.command(name="blame", description="blame a user for raiding.")
    @app_commands.describe(user="The user to blame")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def blame(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer(ephemeral=True)
        loading_msg = await interaction.followup.send("❗ blaming....", ephemeral=True)
        expires_ts = int(time.time()) + 7 * 24 * 60 * 60
        avatar_url = user.display_avatar.url

        class Components(discord.ui.LayoutView):
            container1 = discord.ui.Container(
                discord.ui.Section(
                    discord.ui.TextDisplay(content=f"# {user.mention} ur raid was completed!\nthanks for using **ZNE** bot to raid servers! your trial will end in <t:{expires_ts}:R>"),
                    accessory=discord.ui.Thumbnail(
                        media=avatar_url,
                    ),
                ),
                discord.ui.ActionRow(
                    discord.ui.Button(
                        url="https://discord.gg/4pQzcZxVXK",
                        style=discord.ButtonStyle.link,
                        label="join",
                    ),
                ),
            )

        await interaction.followup.send(view=Components())
        await loading_msg.delete()
        await log_command(interaction, "blame", f"blamed user: {user.id}")

    @app_commands.command(name="say", description="say something through the bot.")
    @app_commands.describe(text="The text for the bot to say")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def say(self, interaction: discord.Interaction, text: str):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("sending..", ephemeral=True)
        await interaction.followup.send(text, ephemeral=False)

    @app_commands.command(name="spam", description="spam something.")
    @app_commands.describe(text="The message to spam")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def spam(self, interaction: discord.Interaction, text: str):
        await interaction.response.defer(ephemeral=True, thinking=True)

        if "discord.gg/" in text.lower():
            text = re.sub(r'(?:https?://)?discord\.gg/\S+', ZNE_INVITE, text)

        await interaction.followup.send(view=make_custom_spam_panel(interaction.user.id, text), ephemeral=True)
        await log_command(interaction, "spam", f"user spammed: {text}")

    @app_commands.command(name="filespam", description="spam a file attachment.")
    @app_commands.describe(attachment="The file to spam")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def filespam(self, interaction: discord.Interaction, attachment: discord.Attachment):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await interaction.followup.send(view=make_filespam_panel(interaction.user.id, attachment), ephemeral=True)
        await log_command(interaction, "filespam", f"user filespammed: {attachment.filename}")


async def setup(bot: commands.Bot):
    await bot.add_cog(RaidCog(bot))
