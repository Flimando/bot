"""
Todo-System Extension für den Discord Bot

Funktionalitäten:
- Verwaltung von Aufgabenlisten pro Server
- Slash-Commands für Hinzufügen/Löschen von Aufgaben
- Automatische Aktualisierung der Todo-Liste
- Berechtigungssystem für Serverzugriff

Befehle:
/todo_add - Neue Aufgabe hinzufügen
/todo_delete - Aufgabe löschen

Datenstruktur:
- Aufgaben werden in data.json unter "todo.Profiles" gespeichert
- Jede Aufgabe hat einen Autor und eine Beschreibung
"""

from discord.ext import commands
from discord import app_commands
import discord
from functions import *
from config import ALLOWED_GUILDS, DISCORD_IDS
class ToDo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='todo_add', description="Fügt eine neue Aufgabe zur Todo-Liste hinzu")
    async def add_task(self, interaction: discord.Interaction, task: str):
        if interaction.guild_id not in ALLOWED_GUILDS["todo"]:
            await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return
        data["todo"]["Profiles"].append({'author': interaction.user.name, 'task': task})
        save_todo_list()
        
        embed = create_embed()
        maf = await interaction.channel.send(embed=embed)
        id = maf.id
        
        if data["todo"]["Last Message ID"] == 0:
            data["todo"]["Last Message ID"] = id
            dump()
        else:
            try:
                message_id = data["todo"]["Last Message ID"]
                msg = await interaction.channel.fetch_message(message_id)
                await msg.delete()
                data["todo"]["Last Message ID"] = id
                dump()
            except discord.NotFound:
                await interaction.response.send_message("Die Nachricht wurde bereits gelöscht.", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("Keine Berechtigung zum Löschen der Nachricht.", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"Ein unerwarteter Fehler ist aufgetreten: {str(e)}", ephemeral=True)
                
        await interaction.response.send_message("Aufgabe hinzugefügt!", ephemeral=True)

    @app_commands.command(name='todo_delete', description="Löscht eine Aufgabe von der Todo-Liste")
    async def delete_task(self, interaction: discord.Interaction, task_id: int):
        if interaction.guild_id not in ALLOWED_GUILDS["todo"]:
            await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return
        if 0 <= task_id < len(data["todo"]["Profiles"]):
            data["todo"]["Profiles"].pop(task_id)
            save_todo_list()
            
            embed = create_embed()
            maf = await interaction.channel.send(embed=embed)
            id = maf.id
            
            try:
                message_id = data["todo"]["Last Message ID"]
                msg = await interaction.channel.fetch_message(message_id)
                await msg.delete()
                data["todo"]["Last Message ID"] = id
                dump()
                await interaction.response.send_message("Aufgabe gelöscht!", ephemeral=True)
            except:
                data["todo"]["Last Message ID"] = id
                dump()
                await interaction.response.send_message("Die zu löschende Nachricht konnte nicht gefunden werden.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Ungültige ID: {task_id}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ToDo(bot))
    print("To-Do Extension Loaded!")