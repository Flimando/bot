"""
Counter Extension für den Discord Bot

Hauptfunktionen:
1. Counter-Setup
    - /setup-counter command
    - Channel-Tracking
    - Counter-Status speichern

2. Counter-Logik
    - Nachrichten auf Zahlen prüfen
    - Reihenfolge prüfen
    - User-Wechsel prüfen
    - Reaktionen senden
    - Fehlermeldungen bei falscher Zahl
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# Datenbank für Counter-Status
COUNTER_DB = "counter_data.json"

class Counter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counter_data = self.load_counter_data()
        
    def load_counter_data(self):
        """Lädt die Counter-Daten aus der JSON-Datei"""
        if os.path.exists(COUNTER_DB):
            with open(COUNTER_DB, 'r') as f:
                return json.load(f)
        return {}
        
    def save_counter_data(self):
        """Speichert die Counter-Daten in die JSON-Datei"""
        with open(COUNTER_DB, 'w') as f:
            json.dump(self.counter_data, f, indent=4)
            
    @app_commands.command(
        name="setup-counter",
        description="Richtet den Counter in diesem Channel ein"
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_counter(self, interaction: discord.Interaction):
        """Richtet den Counter in einem Channel ein"""
        guild_id = str(interaction.guild_id)
        channel_id = str(interaction.channel_id)
        
        # Erstelle Guild-Eintrag falls nicht vorhanden
        if guild_id not in self.counter_data:
            self.counter_data[guild_id] = {}
            
        # Prüfe ob Channel bereits Counter hat
        if channel_id in self.counter_data[guild_id]:
            await interaction.response.send_message("Der Counter ist in diesem Channel bereits aktiv!", ephemeral=True)
            return
            
        self.counter_data[guild_id][channel_id] = {
            "current_number": 0,
            "last_user": None,
            "active": True
        }
        self.save_counter_data()
        
        await interaction.response.send_message("Counter wurde erfolgreich eingerichtet! Beginnt bei 1.", ephemeral=True)
        
    @commands.Cog.listener()
    async def on_message(self, message):
        """Prüft jede Nachricht auf Counter-Relevanz"""
        if message.author.bot:
            return
            
        # Ignoriere DMs (keine Guild)
        if not message.guild:
            return
            
        guild_id = str(message.guild.id)
        channel_id = str(message.channel.id)
        
        # Prüfe ob Server und Channel Counter-aktiv sind
        if (guild_id not in self.counter_data or 
            channel_id not in self.counter_data[guild_id] or 
            not self.counter_data[guild_id][channel_id]["active"]):
            return
            
        try:
            number = int(message.content)
        except ValueError:
            return
            
        counter_info = self.counter_data[guild_id][channel_id]
        expected_number = counter_info["current_number"] + 1
        
        # Prüfe ob die Zahl korrekt ist
        if number == expected_number:
            # Prüfe ob der User sich wiederholt
            if message.author.id == counter_info["last_user"]:
                await message.channel.send(f"{message.author.mention} hat die Kette ruiniert! Der nächste muss bei 1 anfangen!")
                counter_info["current_number"] = 0
                counter_info["last_user"] = None
            else:
                # Alles korrekt, füge Checkmark hinzu
                await message.add_reaction("✅")
                counter_info["current_number"] = number
                counter_info["last_user"] = message.author.id
        else:
            await message.channel.send(f"{message.author.mention} hat die Kette ruiniert! Der nächste muss bei 1 anfangen!")
            counter_info["current_number"] = 0
            counter_info["last_user"] = None
            
        self.save_counter_data()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Counter(bot)) 
"""
Counter Extension für den Discord Bot

Hauptfunktionen:
1. Counter-Setup
    - /setup-counter command
    - Channel-Tracking
    - Counter-Status speichern

2. Counter-Logik
    - Nachrichten auf Zahlen prüfen
    - Reihenfolge prüfen
    - User-Wechsel prüfen
    - Reaktionen senden
    - Fehlermeldungen bei falscher Zahl
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# Datenbank für Counter-Status
COUNTER_DB = "counter_data.json"

class Counter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counter_data = self.load_counter_data()
        
    def load_counter_data(self):
        """Lädt die Counter-Daten aus der JSON-Datei"""
        if os.path.exists(COUNTER_DB):
            with open(COUNTER_DB, 'r') as f:
                return json.load(f)
        return {}
        
    def save_counter_data(self):
        """Speichert die Counter-Daten in die JSON-Datei"""
        with open(COUNTER_DB, 'w') as f:
            json.dump(self.counter_data, f, indent=4)
            
    @app_commands.command(
        name="setup-counter",
        description="Richtet den Counter in diesem Channel ein"
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_counter(self, interaction: discord.Interaction):
        """Richtet den Counter in einem Channel ein"""
        channel_id = str(interaction.channel_id)
        
        if channel_id in self.counter_data:
            await interaction.response.send_message("Der Counter ist in diesem Channel bereits aktiv!", ephemeral=True)
            return
            
        self.counter_data[channel_id] = {
            "current_number": 0,
            "last_user": None,
            "active": True
        }
        self.save_counter_data()
        
        await interaction.response.send_message("Counter wurde erfolgreich eingerichtet! Beginnt bei 1.", ephemeral=True)
        
    @commands.Cog.listener()
    async def on_message(self, message):
        """Prüft jede Nachricht auf Counter-Relevanz"""
        if message.author.bot:
            return
            
        channel_id = str(message.channel.id)
        
        # Prüfe ob Channel Counter-aktiv ist
        if channel_id not in self.counter_data or not self.counter_data[channel_id]["active"]:
            return
        #Checkt ob es eine Zahl ist, wenn nicht gehe in Except return
        try:
            number = int(message.content)
        except ValueError:
            return
            
        counter_info = self.counter_data[channel_id]
        expected_number = counter_info["current_number"] + 1
        
        # Prüfe ob die Zahl korrekt ist
        if number == expected_number:
            # Prüfe ob der User sich wiederholt
            if message.author.id == counter_info["last_user"]:
                await message.channel.send(f"{message.author.mention} hat die Kette ruiniert! Der nächste muss bei 1 anfangen!")
                counter_info["current_number"] = 0
                counter_info["last_user"] = None
            else:
                # Alles korrekt, füge Checkmark hinzu
                await message.add_reaction("✅")
                counter_info["current_number"] = number
                counter_info["last_user"] = message.author.id
        else:
            await message.channel.send(f"{message.author.mention} hat die Kette ruiniert! Der nächste muss bei 1 anfangen!")
            counter_info["current_number"] = 0
            counter_info["last_user"] = None
            
        self.save_counter_data()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Counter(bot)) 