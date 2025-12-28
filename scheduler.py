import asyncio
from datetime import datetime, time, timezone, timedelta
from discord.ext import tasks, commands
import logging

# IST is UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30))

class DailyScheduler(commands.Cog):
    def __init__(self, bot, channel_id, post_callback):
        self.bot = bot
        self.channel_id = channel_id
        self.post_callback = post_callback
        self.daily_task.start()

    def cog_unload(self):
        self.daily_task.cancel()

    @tasks.loop(time=time(hour=8, minute=0, tzinfo=IST)) 
    # Sets the time to 8:00 AM IST. 
    # explicit tzinfo ensures internal conversion to UTC happens correctly.
    async def daily_task(self):
        """Task that runs daily at the specified time."""
        logging.info("Scheduler Triggered: executing daily post.")
        await self.run_post()

    @daily_task.before_loop
    async def before_daily_task(self):
        """Wait until the bot is ready before starting the loop."""
        await self.bot.wait_until_ready()
        logging.info("Scheduler: Bot is ready, task loop started.")

    async def run_post(self):
        """Orchestrates the posting logic."""
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            logging.error(f"Scheduler: Channel {self.channel_id} not found.")
            return

        try:
           await self.post_callback(channel)
        except Exception as e:
            logging.error(f"Scheduler: Error during daily post execution: {e}")

