# Flimando Discord Bot

Ein vielseitiger Discord Bot mit verschiedenen Funktionalitäten für die Flimando Community.

## Hauptfunktionen

### 1. Unix-Befehle
- `/clear` - Löscht eine bestimmte Anzahl von Nachrichten
- `/help` - Zeigt die verfügbaren Befehle an

### 2. To-Do System
- `/todo_add` - Fügt neue Aufgaben zur To-Do-Liste hinzu
- `/todo_delete` - Löscht Aufgaben aus der To-Do-Liste

### 3. Einkaufslisten
- `/shop` - Fügt Artikel zur Einkaufsliste hinzu
- `/ashop` - Löscht Artikel aus der Einkaufsliste

### 4. Ticket-System
- `/ticket_info` - Zeigt Informationen über ein Ticket an
- `/setup_tickets` - Erstellt das Ticket-System in einem bestimmten Kanal

### 5. Port-Informationen
- `/ports` - Zeigt eine Übersicht über die aktuellen Portfreigaben an

### 6. GPT Integration
- `/gpt` - Beantwortet Fragen über die OpenAI-API

Jede Funktionalität ist spezifisch für bestimmte Server freigegeben und durch ein Berechtigungssystem geschützt.

## Technische Details

- Entwickelt mit Python und der discord.py Bibliothek
- Verwendet Slash-Commands für bessere Benutzerinteraktion
- Implementiert ein modulares System mit verschiedenen Extensions
- Nutzt OpenAI's GPT-4 für KI-Funktionalitäten
- Speichert Daten in einer JSON-basierten Datenbank

## Sicherheitsmerkmale

- Server-spezifische Berechtigungssysteme
- Rate-Limiting für Nachrichtenlöschung
- Ephemeral Responses für sensible Befehle
- Geschützte Zugriffe auf sensible Informationen

## Entwickelt von
[Darcci](https://github.com/Darcci) und [Flimanda](https://github.com/flimanda)
stellvertretend für Flimando - https://flimando.com/ 