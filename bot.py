import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
import asyncio

# Service Imports
from striver_loader import StriverLoader
from leetcode_service import LeetCodeService
from scheduler import DailyScheduler

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load Env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', 0))

if not TOKEN or CHANNEL_ID == 0:
    logging.error("Environment variables DISCORD_TOKEN or CHANNEL_ID are missing.")
    exit(1)

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.command(name='dsahelp', aliases=['commands', 'bothelp'])
async def help_command(ctx):
    """Shows this help message."""
    embed = discord.Embed(
        title="🤖 Bot Commands Help",
        description="Here are the available commands to interact with the Daily DSA Bot.",
        color=0x3498db,
        timestamp=datetime.datetime.now()
    )
    
    commands_list = [
        ("!daily", "Post today's problem (auto-selects source based on schedule)"),
        ("!leetcode", "Fetch today's official LeetCode Daily Challenge"),
        ("!striver", "Get a random new problem from the Striver DSA sheet"),
        ("!topic <name>", "Get a random Striver problem from a specific topic (e.g. `!topic Arrays`)"),
        ("!stats", "View repository statistics (Total/Posted/Remaining)"),
        ("!dsahelp", "Show this help message (Aliases: !commands)")
    ]
    
    for name, desc in commands_list:
        embed.add_field(name=name, value=desc, inline=False)
        
    embed.set_footer(text="Happy Coding! 🚀")
    await ctx.send(embed=embed)

# Initialize Services
striver_loader = StriverLoader()
leetcode_service = LeetCodeService()

async def post_daily_problem(channel, source_override=None):
    """
    Logic to determine which problem to post and send it to Discord.
    source_override: 'leetcode' or 'striver' to force a specific source.
    """
    # For now, simple logic: Alternate or just fetch LeetCode for today?
    # Let's try to do both or customizable. The prompt suggested "One question per day".
    # Let's implement a random choice or day-based rotation if no override.
    
    # Simple strategy: Even days = LeetCode, Odd days = Striver
    import datetime
    day_of_month = datetime.datetime.now().day
    
    source = source_override
    if not source:
        source = "leetcode" if day_of_month % 2 == 0 else "striver"
        
    embed = None
    
    if source == 'leetcode':
        data = leetcode_service.get_daily_challenge()
        if data:
            embed = discord.Embed(
                title=f"🚀 Daily LeetCode Challenge: {data['title']}",
                url=data['link'],
                color=0xf0ad4e, # Orange-ish for LC
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Difficulty", value=data['difficulty'], inline=True)
            embed.add_field(name="Topic", value=", ".join(data['topics']) or "N/A", inline=True)
            embed.add_field(name="Date", value=data['date'], inline=False)
            embed.set_footer(text="Solve it now on LeetCode!")
        else:
            logging.error("Failed to fetch LeetCode data.")
            await channel.send("Could not fetch LeetCode Daily data today. :(")
            return

    elif source == 'striver':
        data = striver_loader.get_random_question()
        if data:
            embed = discord.Embed(
                title=f"💡 Striver DSA: {data['title']}",
                url=data['link'],
                color=0x2ecc71, # Green
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Difficulty", value=data['difficulty'], inline=True)
            embed.add_field(name="Topic", value=data['topic'], inline=True)
            embed.set_footer(text=f"Striver Sheet | ID: {data['id']}")
            
            # Mark as posted
            striver_loader.mark_as_posted(data['id'])
        else:
            logging.info("No new Striver questions available.")
            await channel.send("All Striver questions have been posted! Time to restock.")
            return

    if embed:
        await channel.send(embed=embed)


@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    logging.info('-------------------------------------------')
    
    # Initialize Scheduler
    # We pass the bot, channel_id, and the callback function for posting
    await bot.add_cog(DailyScheduler(bot, CHANNEL_ID, post_daily_problem))


@bot.command(name='daily')
async def daily(ctx):
    """Manually triggers the daily post."""
    logging.info(f"Manual trigger by {ctx.author}")
    await post_daily_problem(ctx.channel)

@bot.command(name='leetcode')
async def leetcode_command(ctx):
    """Fetches today's LeetCode challenge."""
    await post_daily_problem(ctx.channel, source_override='leetcode')

@bot.command(name='striver')
async def striver_command(ctx):
    """Fetches a random unique Striver problem."""
    await post_daily_problem(ctx.channel, source_override='striver')

@bot.command(name='topic')
async def topic_command(ctx, *, topic_name: str):
    """Fetches a random Striver problem from a specific topic."""
    # We need to expose a method in StriverLoader to filter by topic, which we did: get_random_question(topic=...)
    # But post_daily_problem logic needs to handle this specific request.
    # The simplest way is to fetch the data here and use the embed logic, or refactor post_daily_problem.
    # Refactoring slightly to reuse embed logic is cleaner, but for now copying is faster/safer or just call loader directly.
    
    data = striver_loader.get_random_question(topic=topic_name)
    
    if data:
        embed = discord.Embed(
            title=f"💡 Striver DSA ({data['topic']}): {data['title']}",
            url=data['link'],
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Difficulty", value=data['difficulty'], inline=True)
        embed.add_field(name="Topic", value=data['topic'], inline=True)
        embed.set_footer(text=f"Striver Sheet | ID: {data['id']}")
        
        # We generally might NOT want to mark manual topic requests as "posted" to avoid burning through the list
        # for daily consumption, OR successful solve = posted.
        # Let's decide NOT to mark it to keep the daily schedule fresh.
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"No questions found for topic: **{topic_name}** (or all posted).")

@bot.command(name='stats')
async def stats_command(ctx):
    """Shows stats about the question bank."""
    stats = striver_loader.get_question_stats()
    msg = (
        f"**Repository Stats**\n"
        f"Total Questions: {stats['total']}\n"
        f"Posted: {stats['posted']}\n"
        f"Remaining: {stats['remaining']}"
    )
    await ctx.send(msg)

if __name__ == "__main__":
    bot.run(TOKEN)
