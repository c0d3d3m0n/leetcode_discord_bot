# Deployment Guide

To keep your bot running 24/7, you need to "host" it on a cloud server. Here are the two easiest and most popular options.

## Option 1: Railway (Recommended for Ease)
Railway is very easy to set up and works great for Discord bots.

1.  **Push your code to GitHub**:
    -   Create a new repository on GitHub.
    -   Push this entire `discord-dsa-bot` folder to it.
2.  **Sign up at [Railway.app](https://railway.app/)**.
3.  **New Project** -> **Deploy from GitHub repo**.
4.  Select your repository.
5.  **Variables**:
    -   Go to the "Variables" tab in your Railway project dashboard.
    -   Add `DISCORD_TOKEN` and paste your token.
    -   Add `CHANNEL_ID` and paste your channel ID.
6.  **Deploy**: Railway will detect the `Procfile` or `requirements.txt` and start your bot.

## Option 2: Render (Good Alternative)
Render has a "Background Worker" type nice for bots.

1.  **Push to GitHub** (same as above).
2.  **Sign up at [Render.com](https://render.com/)**.
3.  Click **New +** -> **Background Worker**.
    -   *Note: Do not choose "Web Service", bots are background workers.*
4.  Connect your GitHub repo.
5.  **Settings**:
    -   **Runtime**: Python 3
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `python bot.py`
6.  **Environment Variables**:
    -   Scroll down to "Advanced" or "Environment".
    -   Add `DISCORD_TOKEN` and `CHANNEL_ID`.
7.  **Create Service**.

## Option 3: VPS (DigitalOcean / AWS) - Advanced
If you have a Linux server (Ubuntu):

1.  Clone your repo: `git clone ...`
2.  Install python/pip.
3.  Install dependencies: `pip install -r requirements.txt`
4.  Use `systemd` to keep it running:
    -   Create a file `/etc/systemd/system/discordbot.service`
    ```ini
    [Unit]
    Description=Discord Bot
    After=network.target

    [Service]
    User=root
    WorkingDirectory=/root/discord-dsa-bot
    ExecStart=/usr/bin/python3 /root/discord-dsa-bot/bot.py
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
5.  `systemctl enable discordbot`
6.  `systemctl start discordbot`
