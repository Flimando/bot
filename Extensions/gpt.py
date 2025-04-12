"""
OpenAI GPT Integration für den Discord Bot

Hauptfunktionen:
1. GPT-4 API Integration
    - Verarbeitung von Benutzeranfragen
    - Kommunikation mit OpenAI API
    - Token-Verbrauch Tracking

2. Berechtigungssystem
    - Server-spezifische Zugriffskontrolle
    - Bot-Benutzer Filterung
    - Fehlerbehandlung

3. Antwortverarbeitung
    - Formatierte Ausgabe der GPT Antworten
    - Logging des Token-Verbrauchs
    - Fehlerbehandlung bei API-Problemen

Konfiguration:
- Verwendet OpenAI API Key aus config.py
- Zugriffskontrolle über ALLOWED_GUILDS
"""

# Grundlegende Imports für die GPT-Funktionalität
import os, discord, openai, time
from discord import app_commands
from openai import OpenAI
from functions import *
from config import openai_api_key, ALLOWED_GUILDS

# OpenAI API Key aus der Konfiguration
OPENAI_API_KEY = openai_api_key

class GPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='gpt', 
        description='Beantwortet Fragen über die OpenAI-API.'
    )
    async def gpt_command(self, interaction: discord.Interaction, *, query: str):
        # Ignoriere Bot-Benutzer
        if interaction.user.bot:
            return

        # Prüfe Serverberechtigungen
        if interaction.guild_id not in ALLOWED_GUILDS["gpt"]:
            await interaction.response.send_message(
                "Du hast keine Berechtigung, diesen Befehl auszuführen.", 
                ephemeral=True
            )
            return

        # Initialisiere OpenAI Client
        client = OpenAI(
            api_key=OPENAI_API_KEY,
        )

        # Sende Anfrage an GPT-4
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Well its something at least
            messages=[
                {"role": "user", "content": query}
            ]
        )

        # Verarbeite und sende Antwort
        answer = response.choices[0].message.content
        
        # Logge Token-Verbrauch für Monitoring
        print(f"Verbrauchte Tokens: {response.usage.completion_tokens}  Text: {query}")
        
        # Sende Antwort an Discord
        await interaction.response.send_message(answer)

# Setup-Funktion für Discord.py
async def setup(bot):
    await bot.add_cog(GPT(bot))
    print("GPT Extension Loaded!")