"""
Shopping-Listen Extension für den Discord Bot

Funktionalitäten:
1. Einkaufslisten-Verwaltung
    - Hinzufügen von Artikeln
    - Automatische Aktualisierung der Liste
    - Benutzer-Attribution

2. Nachrichtenverwaltung
    - Automatisches Löschen alter Listen
    - Aktualisierung der letzten Listen-Nachricht
    - Embed-basierte Darstellung

Berechtigungen:
- Nur in spezifischen Servern verfügbar
- Konfigurierbar über ALLOWED_GUILDS
"""

from discord.ext import commands
import discord
from discord import app_commands
from functions import *
from config import COLORS, DISCORD_IDS, ALLOWED_GUILDS

class Shopping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="shop",
        description="Fügt einen Artikel zur Einkaufsliste hinzu"
    )
    async def add_task(self, interaction: discord.Interaction, task: str):
        if interaction.guild_id not in ALLOWED_GUILDS["shopping"]:
            await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return
        data["shopping"]["Profiles"].append({
            'author': interaction.user.name, 
            'task': task
        })
        save_shopping_list()
        
        embed = create_shopping_embed()
        await interaction.response.send_message(embed=embed)
        
        # Speichere die neue Nachricht-ID
        message = await interaction.original_response()
        if data["shopping"]["Last Message ID"] == 0:
            data["shopping"]["Last Message ID"] = message.id
            shopping_dump()
        else:
            try:
                old_message_id = data["shopping"]["Last Message ID"]
                old_message = await interaction.channel.fetch_message(old_message_id)
                await old_message.delete()
            except discord.NotFound:
                print(f"Nachricht {old_message_id} nicht gefunden")
            except discord.Forbidden:
                await interaction.response.send_message("Keine Berechtigung zum Löschen", ephemeral=True)
            except Exception as e:
                print(f"Unerwarteter Fehler: {e}")
            finally:
                data["shopping"]["Last Message ID"] = message.id
                shopping_dump()

    @app_commands.command(
        name="ashop",
        description="Löscht einen Artikel von der Einkaufsliste"
    )
    async def delete_task(self, interaction: discord.Interaction, task_id: int):
        if interaction.guild_id not in ALLOWED_GUILDS["shopping"]:
            await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return
        if 0 <= task_id < len(data["shopping"]["Profiles"]):
            data["shopping"]["Profiles"].pop(task_id)
            save_shopping_list()
            
            embed = create_shopping_embed()
            await interaction.response.send_message(embed=embed)
            
            # Update die Nachricht-ID und lösche die alte
            message = await interaction.original_response()
            old_message_id = data["shopping"]["Last Message ID"]
            try:
                old_message = await interaction.channel.fetch_message(old_message_id)
                await old_message.delete()
            except discord.NotFound:
                print(f"Nachricht {old_message_id} nicht gefunden")
            except discord.Forbidden:
                print("Keine Berechtigung zum Löschen der Nachricht")
            except Exception as e:
                print(f"Unerwarteter Fehler beim Löschen: {e}")
            data["shopping"]["Last Message ID"] = message.id
            shopping_dump()
        else:
            await interaction.response.send_message(
                f"Ungültige ID: {task_id}", 
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Shopping(bot))
    print("Shopping Extension Loaded!")