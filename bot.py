import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
import asyncio
import datetime

# Service Imports
from striver_loader import StriverLoader
from leetcode_service import LeetCodeService
from scheduler import DailyScheduler
from code_runner import CodeRunner

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
        description="Here are the available commands to interact with the Daily DSA Bot.\n\n[**Join our Discord Server!**](https://discord.gg/ucRc7Drv)",
        color=0x3498db,
        timestamp=datetime.datetime.now()
    )
    
    commands_list = [
        ("!daily", "Post today's problem (auto-selects source based on schedule)"),
        ("!leetcode", "Fetch today's official LeetCode Daily Challenge"),
        ("!striver", "Get a random new problem from the Striver DSA sheet"),
        ("!topic <name>", "Get a random Striver problem from a specific topic (e.g. `!topic Arrays`)"),
        ("!stats", "View repository statistics (Total/Posted/Remaining)"),
        ("!submit", "Run code snippets (use markdown blocks, e.g. ```python ... ```)"),
        ("!dsahelp", "Show this help message (Aliases: !commands)")
    ]
    
    for name, desc in commands_list:
        embed.add_field(name=name, value=desc, inline=False)
    
    # Add Invite Link
    invite_url = f"https://discord.com/api/oauth2/authorize?client_id={ctx.bot.user.id}&permissions=274877908992&scope=bot"
    embed.add_field(name="🔗 Add Me", value=f"[Click here to invite me to your server]({invite_url})", inline=False)

    embed.set_footer(text="Happy Coding! 🚀")
    await ctx.send(embed=embed)

# Initialize Services
striver_loader = StriverLoader()
leetcode_service = LeetCodeService()
code_runner = CodeRunner()

@bot.command(name='submit')
async def submit_command(ctx, *, code_block: str = None):
    """
    Executes code provided in a markdown block.
    Usage: !submit ```python print('hello') ```
    """
    if not code_block:
        await ctx.send("Please provide code in a markdown block! Example:\n!submit\n\\`\\`\\`python\nprint('Hello')\n\\`\\`\\`")
        return

    # cleaner parsing of the code block
    import re
    # Flexible regex:
    # 1. ``` : primitive start
    # 2. ([a-zA-Z0-9+\-#]*) : Optional language (allow chars like +, # for c++, c#)
    # 3. \s+ : At least one whitespace (newline usually)
    # 4. (.*?) : The code
    # 5. ``` : End
    match = re.search(r"```([a-zA-Z0-9+\-#]*)\s+(.*?)```", code_block, re.DOTALL)
    
    if not match:
        # Fallback: Maybe they didn't put a language? or formatting is slightly off
        # Let's try to just find content between ``` and ```
        match = re.search(r"```(.*?)```", code_block, re.DOTALL)

    if not match:
         await ctx.send("Could not parse code block. Ensure you use \\`\\`\\`language ... \\`\\`\\` formatting.")
         return

    language = match.group(1) if len(match.groups()) > 1 else "python"
    # If the regex was the fallback one, group 1 is the code
    if len(match.groups()) == 1:
         code = match.group(1)
         language = "python" # default to python if generic block
    else:
        # standard case
        language = match.group(1) or "python"
        code = match.group(2)
        
    # Clean up language string (sometimes has whitespace if regex was loose)
    language = language.strip()

    msg = await ctx.send(f"Running {language} code... ⏳")
    
    result = code_runner.execute_code(language, code)
    
    if "error" in result:
        await msg.edit(content=f"❌ Execution Error: {result['error']}")
        return

    # prepare output
    output = result.get('output', '')
    if len(output) > 1900:
        output = output[:1900] + "... (truncated)"
    elif not output:
        output = "(No Output)"

    embed = discord.Embed(
        title=f"RUN: {result.get('code') == 0 and '✅ Success' or '⚠️ Error'}",
        color= result.get('code') == 0 and 0x2ecc71 or 0xe74c3c
    )
    embed.add_field(name="Output", value=f"```\n{output}\n```", inline=False)
    embed.set_footer(text=f"Language: {language}")

    await msg.edit(content=None, embed=embed)


async def post_daily_problem(channel, source_override=None, topic_filter=None):
    """
    Logic to determine which question to post.
    """
    import datetime
    day_of_month = datetime.datetime.now().day
    
    source = source_override
    if not source:
        source = "leetcode" if day_of_month % 2 == 0 else "striver"
        
    embed = None
    
    if source == 'leetcode':
        # LeetCode logic (unchanged)
        data = leetcode_service.get_daily_challenge()
        if data:
            embed = discord.Embed(
                title=f"🚀 Daily LeetCode Challenge: {data['title']}",
                url=data['link'],
                color=0xf0ad4e,
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
        # Pass topic_filter if provided
        data = striver_loader.get_random_question(topic_filter=topic_filter)
        if data:
            embed = discord.Embed(
                title=f"💡 Striver DSA: {data['title']}",
                url=data['link'],
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Difficulty", value=data['difficulty'], inline=True)
            embed.add_field(name="Topic", value=data['topic'], inline=True)
            embed.set_footer(text=f"Striver Sheet | ID: {data['id']}")
            
            # Mark as posted
            striver_loader.mark_as_posted(data['id'])
        else:
            if topic_filter:
                 await channel.send(f"No available questions found for topic: **{topic_filter}** (or all posted).")
            else:
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
    # Explicitly force 'leetcode' source for the daily schedule as requested
    async def scheduled_post_wrapper(channel):
        await post_daily_problem(channel, source_override='leetcode')
        
    await bot.add_cog(DailyScheduler(bot, CHANNEL_ID, scheduled_post_wrapper))


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
    """Get a random Striver problem from a specific topic."""
    await post_daily_problem(ctx.channel, source_override='striver', topic_filter=topic_name)

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
