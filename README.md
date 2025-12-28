# Daily DSA & LeetCode Discord Bot

A Python-based Discord bot designed to foster daily coding habits by automatically posting problems from a curated Striver DSA list and LeetCode's Daily Coding Challenge.

## Features

chna

## Setup & Installation

### Prerequisites
- Python 3.10+
- A Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd discord-dsa-bot
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**
   Create a `.env` file in the root directory:
   ```env
   DISCORD_TOKEN=your_token_here
   CHANNEL_ID=your_channel_id_here
   ```

4. **Populate Data**
   Ensure `data/striver_questions.json` is present with the question list.

5. **Invite the Bot**
   Use your generated OAuth2 URL (with `bot` and `applications.commands` scopes) to invite the bot to your server. 
   - Ensure it has permissions to **Send Messages** and **Embed Links** in the target channel.

6. **Run the Bot**
   ```bash
   python bot.py
   ```

## Project Structure

- `bot.py`: Main entry point and Discord client.
- `leetcode_service.py`: Handles LeetCode GraphQL API fetching.
- `striver_loader.py`: Manages local JSON question selection and state.
- `scheduler.py`: Handles timing and periodic tasks.
- `data/`: Stores problem lists and history.

## Sharing the Bot
To add this bot to another server, send this Invite Link to the server admin:
[**Invite Bot**](https://discord.com/oauth2/authorize?client_id=1454710862458650678&permissions=8&scope=bot%20applications.commands)

**Note:**
- **Commands** (`!daily`, `!striver`, etc.) will work in **any** server the bot is in.
- **Automatic Auto-Posting** will currently only happen in the single channel defined in `CHANNEL_ID` (your main server).

## Contributing

Feel free to fork and submit PRs!
