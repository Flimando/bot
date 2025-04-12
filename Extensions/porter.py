"""
Port-Informations Extension für den Discord Bot

Funktionalitäten:
1. Port-Anzeige
    - Auflistung aller wichtigen Ports
    - Formatierte Embed-Darstellung
    - Kategorisierte Port-Informationen

2. Sicherheit
    - Nur in autorisierten Kanälen verfügbar
    - Beschränkter Zugriff auf Admin-Server
    - Sensitive Daten Schutz

Konfiguration:
- Ports werden in data.json definiert
- Farben und Layout über COLORS konfiguriert, COLORS ist in config.py definiert
"""

from discord.ext import commands
import discord
from discord import app_commands
from functions import *
from config import DISCORD_IDS, COLORS, ALLOWED_GUILDS

class Porter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ports",
        description="Zeigt die Port-Informationen an"
    )
    async def ports(self, interaction: discord.Interaction):
        if interaction.guild_id not in ALLOWED_GUILDS["ports"]: #Only Admin because of the sensitive data
            await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return
        # Hole die Port-Daten aus der data.json
        embed_data = data["embeds"]["ports"]
        
        embed = discord.Embed(
            title=embed_data["title"],
            color=COLORS["violet"],
            timestamp=get_timestamp()
        )

        # Füge alle Felder hinzu
        for field in embed_data["fields"]:
            embed.add_field(
                name=field["name"], 
                value=field["value"], 
                inline=False
            )

        # Setze Footer wenn vorhanden
        if "footer" in embed_data and "icon_url" in embed_data["footer"]:
            embed.set_footer(icon_url=embed_data["footer"]["icon_url"])
        
        # Sende nur im richtigen Kanal
        ports_channel = DISCORD_IDS["ports_channel"]  # Liegt in config.py
        if interaction.channel_id == ports_channel:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                "Dieser Befehl kann nur im dafür vorgesehenen Kanal verwendet werden.", 
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Porter(bot))
    print("Porter Extension Loaded!")