"""
Unix-Befehle Extension für den Discord Bot

Funktionalitäten:
1. Clear Command
    - Löscht eine bestimmte Anzahl von Nachrichten
    - Verfügbar auf allen erlaubten Servern
    - Verzögertes Löschen zur Vermeidung von Rate Limits

Sicherheitshinweise:
- Purge-Funktion sollte mit Bedacht verwendet werden
- Automatische Verzögerungen eingebaut
- Ephemeral Responses für bessere Übersicht
"""

from discord.ext import commands
import discord
import asyncio
from discord import app_commands
from functions import *
from config import COLORS, BOT_CONFIG, ALLOWED_GUILDS, GUILD_IDS

prefix = BOT_CONFIG["prefix"]

class Unix(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Logged Succesfully In")
        await self.bot.change_presence(status = discord.Status.online, activity=discord.Activity(type = discord.ActivityType.playing, name = "mit dem kleinen süssen Debian"))
    
    @app_commands.command(
        name="help",
        description="Zeigt die Hilfe an"
    )
    async def help(self, interaction: discord.Interaction, category: str = None):
        if interaction.guild_id not in ALLOWED_GUILDS["unix"]:
            await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return
        if interaction.guild_id == int(GUILD_IDS["flimando_admin"]):
            embed = discord.Embed(
                title="Hilfe - Befehle", 
                description="Hier sind die verfügbaren Befehle:", 
                color=COLORS["violet"], 
                timestamp=get_timestamp()
            )
            
            embed.add_field(name="/help", value="Ruft dieses Menü auf.", inline=False)
            embed.add_field(name="/clear", value="Löscht eine bestimmte Anzahl von Nachrichten.", inline=False)
            embed.add_field(name="/todo_add", value="Fügt Aufgaben zu einer To-Do-Liste hinzu.", inline=False)
            embed.add_field(name="/todo_delete", value="Löscht Aufgaben aus der To-Do-Liste.", inline=False)
            embed.add_field(name="/shop", value="Fügt Items zu einer Shopping-Liste hinzu.", inline=False)
            embed.add_field(name="/ashop", value="Löscht Items aus der Shopping-Liste.", inline=False)
            embed.add_field(name="/ports", value="Ruft eine Übersicht über die aktuelle Portfreigaben auf.", inline=False)
            embed.add_field(name="/gpt", value="Beantwortet Fragen über die OpenAI-API.", inline=False)
            
            await interaction.response.send_message(embed=embed)
        elif interaction.guild_id == int(GUILD_IDS["flimando_server"]):
            embed = discord.Embed(
                title="Hilfe - Befehle", 
                description="Hier sind die verfügbaren Befehle:", 
                color=COLORS["violet"], 
                timestamp=get_timestamp()
            )
            embed.add_field(name="/help", value="Ruft dieses Menü auf.", inline=False)
            embed.add_field(name="/clear", value="Löscht eine bestimmte Anzahl von Nachrichten.", inline=False)
            embed.add_field(name="/ticket_info", value="Zeigt Informationen über ein Ticket an.", inline=False)
            embed.add_field(name="/setup_tickets", value="Erstellt das Ticket-System in einem bestimmten Kanal.", inline=False)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Du befindest dich nicht in einem der Server, in denen du diesen Befehl benutzen kannst.", ephemeral=True)

    @app_commands.command(
        name = "clear",
        description = "Löscht eine bestimmte Anzahl von Nachrichten"
    ) #Kann überall benutzt werden weil nicht extrem wichtig
    async def clear(self, interaction: discord.Interaction, amount: int):
        # Defer the response to avoid timeout
        await interaction.response.defer(ephemeral=True)
        
        # Warte kurz vor dem Purge
        await asyncio.sleep(1)
        
        # Führe Purge aus
        deleted = await interaction.channel.purge(limit=amount)
        
        # Warte nach dem Purge
        await asyncio.sleep(1)
        
        # Sende Bestätigung
        await interaction.followup.send(
            f"Die letzten {len(deleted)} Nachrichten wurden gelöscht",
            ephemeral=True
        )



async def setup(bot):
    await bot.add_cog(Unix(bot))
    print("Unix Extension Loaded!")
