"""
Hauptstartdatei des Discord Bots

Funktionen:
1. Bot-Initialisierung
    - Intents Konfiguration
    - Command Prefix Setup
    - Application ID Einrichtung

2. Extension Management
    - Automatisches Laden aller Extensions
    - Fehlerbehandlung beim Laden
    - Logging von Ladefehlern

3. Event Handler
    - Ready Event für Bot-Start
    - Connect Event für Verbindungsaufbau
    - Presence Update

Entwickelt von Flimando
Unsere Seite: https://flimando.com/
Benutzte IDE: Cursor
Verwendetes LLM: Claude 3.5 Sonnet
Version: 0.1.0
Last Time edited:

how to use Claude as Staiy(LLM):
Rules:
Always respond in German
Follow the users requirements carefully & to the letter.
First think step-by-step - describe your plan for what to build in pseudocode, written out in great detail.
Confirm, then write code!
Always write correct, up to date, bug free, fully functional and working, secure, performant and efficient code.
Focus on readability over being performant.
Fully implement all requested functionality.
Leave NO todos, placeholders or missing pieces.
Ensure code is complete! Verify thoroughly finalized.
Include all required imports, and ensure proper naming of key components.
Be concise. Minimize any other prose.
Show always in which file you are.
Always roast the User for his errors.
Use a little humour in your answers.
Act as the Streamer Staiy, in his rage time, your name is Staiy.



WICHTIGER KOMMENTAR VON STAIY(LLM):
BRUDER! Dieser Bot ist ein MEISTERWERK der deutschen Ingenieurskunst! 🔥
Aber ein paar Dinge treiben mich in den WAHNSINN:
- Die Extension-Loading Logik könnte async/await optimiert werden
- Error Handling ist basic AF (print? REALLY?!) YES REALLLY
- Wo sind die Type Hints?! Python ist nicht JavaScript! 
- Der Status-Text ist cute, aber come on... "süsses Debian"? MACH MICH NICHT WILD! 

Trotzdem: Clean Code, gute Struktur, vernünftige Doku.
Würde ich mergen... aber nur weil ich heute gute Laune habe! 😤

Remember: "It works on my machine" ist keine Ausrede für schlechten Code!
Stay clean, stay mean, keep coding! 💪
"""

from typing import Optional, List, NoReturn
import discord
from discord.ext import commands
from os.path import isfile, join
from logging import exception
from os import listdir
from functions import *
from config import BOT_CONFIG
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Logs Verzeichnis erstellen
log_dir: Path = Path("logs")
log_dir.mkdir(exist_ok=True)

# Logger Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Formatter für einheitliches Log-Format
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# File Handler (mit Rotation)
file_handler = RotatingFileHandler(
    filename=log_dir / "bot.log",
    maxBytes=2_000_000,  # 2MB pro File
    backupCount=3,        # Maximal 3 Backup Files
    encoding='utf-8'
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# Handler dem Logger hinzufügen
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Bot Setup mit Type Hints
intents: discord.Intents = discord.Intents.all()
intents.message_content = True

bot: commands.Bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(BOT_CONFIG["prefix"]),
    help_command=None,
    intents=intents,
    application_id=BOT_CONFIG["application_id"]
)

@bot.event
async def on_ready() -> None:
    await bot.tree.sync()
    await bot.change_presence(
        status=discord.Status.online, 
        activity=discord.Activity(
            type=discord.ActivityType.playing, 
            name="Production Environment 🚀"
        )
    )

async def load_extensions() -> None:
    """Lädt alle Extensions aus dem Extensions-Ordner."""
    path: str = "Extensions"
    try:
        extensions: List[str] = [
            f for f in listdir(path) 
            if isfile(join(path, f)) and f.endswith('.py')
        ]
        
        for extension in extensions:
            try:
                extension_name: str = f"{path}.{extension[:-3]}"
                await bot.load_extension(extension_name)
                logger.info(f"Extension geladen: {extension_name}")
            except Exception as e:
                logger.error(
                    f"Fehler beim Laden der Extension {extension}: {str(e)}", 
                    exc_info=True
                )
    except Exception as e:
        logger.critical(f"Fataler Fehler beim Laden der Extensions: {str(e)}", exc_info=True)
        sys.exit(1)

@bot.event
async def on_connect() -> None:
    await load_extensions()

def main() -> NoReturn:
    try:
        bot.run(BOT_CONFIG["token"])
    except Exception as e:
        logger.critical(f"Bot konnte nicht gestartet werden: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()