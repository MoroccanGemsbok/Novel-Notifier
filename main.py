import scraping
import discord
import os
import datetime
from dotenv import load_dotenv
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.message_content = True
load_dotenv()
bot = commands.Bot(command_prefix='!', intents=intents)
prev = []
urls = []


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("the notifying game!"))
    user = await bot.fetch_user(int(os.getenv('USER_ID')))
    scrape.start(user)
    print(f'We have logged in as {bot.user}')


@bot.command()
async def ping(ctx):
    await ctx.send(f'Here is the ping: {round(bot.latency * 1000)} ms')


@bot.command()
async def add(ctx, url):
    urls.append(url)
    prev.append("")
    await ctx.send(f'Added **{scraping.scrape_title(url)}** to the reading list')


@bot.command()
async def remove(ctx, index):
    i = int(index) - 1
    if i < 0 or i >= len(urls):
        await ctx.send(f'Index out of bounds')
        return
    prev.pop(i)
    url = urls.pop(i)
    await ctx.send(f'Removed **{scraping.scrape_title(url)}** from the reading list')


@bot.command()
async def novels(ctx):
    text = ""
    if len(urls) == 0:
        await ctx.send("No novels in the reading list.\nAdd one with !add <url>")
        return
    for i in range(len(urls)):
        index = i + 1
        text += "**" + str(index) + "** - " + scraping.scrape_title(urls[i]) + "\n"
    await ctx.send(f'Reading List:\n {text}')


@tasks.loop(time=[datetime.time(hour=i) for i in range(24)])
async def scrape(user):
    await bot.wait_until_ready()
    print("running scrape")
    if urls:
        for i in range(len(urls)):
            url = urls[i]
            con = scraping.scrape_link(url)
            if con != prev[i]:
                prev[i] = con

                embed = discord.Embed(title="**" + scraping.scrape_title(url) + "**",
                                      url=con,
                                      description=scraping.scrape_chapter_title(url),
                                      colour=0x85c5db,
                                      timestamp=datetime.datetime.now())
                embed.set_author(name="Novel Notifier")
                embed.set_thumbnail(url=scraping.scrape_thumbnail(url))

                await user.send(user.mention, embed=embed)
            # else:
            #     await user.send(f'No new chapters for {scraping.scrape_title(url)}')


bot.run(os.getenv('BOT_ID'))
