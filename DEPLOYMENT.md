# Deployment Guide

To keep your bot running 24/7, you need to "host" it on a cloud server. Since Render's Background Workers are improved and paid, here are the best **FREE** alternatives for 2024/2025.

## Option 1: Fly.io (Free Allowance)
Fly.io is currently one of the best options for running Docker containers for free.
*Requires a credit card for sign-up (security check), but the free allowance is generous.*

1.  **Install `flyctl`**: Download the CLI tool from [fly.io/docs/hands-on/install-flyctl](https://fly.io/docs/hands-on/install-flyctl/).
2.  **Signup/Login**: Run `fly auth signup` or `fly auth login`.
3.  **Launch**: Open a terminal in this project folder and run:
    ```bash
    fly launch
    ```
    *   It will detect the `Dockerfile`.
    *   Choose a region near you.
    *   **Say NO** to Postgres/Redis if asked (you don't need them).
4.  **Set Secrets**:
    Set your discord token and channel ID as secrets.
    ```bash
    fly secrets set DISCORD_TOKEN=your_token_here
    fly secrets set CHANNEL_ID=your_channel_id_here
    ```
5.  **Deploy**:
    ```bash
    fly deploy
    ```

## Option 2: Oracle Cloud "Always Free" (Best Value, Harder Setup)
Oracle Cloud offers a very generous "Always Free" tier (4 ARM CPUs, 24GB RAM) which is a full Linux server (VPS).
*Sign-up can be strict about cards/locations.*

1.  Sign up for **Oracle Cloud Free Tier**.
2.  Create a **VM instance** (choose the "Always Free" eligible **Ampere** shape).
3.  **SSH into your server**.
4.  Follow the **Option 3: VPS / Self-Hosting** instructions below.

## Option 3: VPS / Self-Hosting (Raspberry Pi / Old Laptop)
If you have a Raspberry Pi, an old laptop, or a Linux VPS (DigitalOcean, AWS, Oracle), this is the most reliable free method.

1.  **Clone your repo** to the machine: `git clone <your-repo-url>`
2.  **Install Python**: Ensure Python 3.10+ is installed.
3.  **Install Dependencies**: `pip install -r requirements.txt`
4.  **Keep it Running with Systemd (Linux)**:
    *   Create a file `/etc/systemd/system/discordbot.service`
    ```ini
    [Unit]
    Description=Daily DSA Discord Bot
    After=network.target

    [Service]
    # Update User and Directory to match your setup!
    User=root
    WorkingDirectory=/root/leetcode_discord_bot
    ExecStart=/usr/bin/python3 /root/leetcode_discord_bot/bot.py
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
5.  **Enable and Start**:
    ```bash
    sudo systemctl enable discordbot
    sudo systemctl start discordbot
    ```

## Legacy Options (Now Paid/Limited)
*   **Render**: "Background Workers" costs $7/month. Free tier only for Web Services (which sleep).
*   **Railway**: $5 trial credit only, then paid.
*   **Heroku**: No longer has a free tier.
