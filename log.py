import discord
from discord.ext import commands
import datetime
import pytz
import requests
from flask import Flask
from threading import Thread

# -----------------------------------------

app = Flask("")


@app.route("/")
def home():
    return "Hello. I am alive!"


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


# -----------------------------------------

r = requests.head(url="https://discord.com/api/v1")
try:
    print(f"Rate limit {int(r.headers['Retry-After']) / 60} minutes left")
except:
    print("No rate limit")

# -----------------------------------------

intents = discord.Intents.default()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix="*", intents=intents, description="Developer: @D1STANG3R")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(f"Log {len(bot.guilds)}"), status=discord.Status.online)
    print("Connected to bot: {}".format(bot.user.name))
    print("Bot ID: {}".format(bot.user.id))


@bot.event
async def on_guild_join(guild):
    await bot.change_presence(activity=discord.Game(f"Log {len(bot.guilds)}"), status=discord.Status.online)
    if guild.system_channel is not None:
        await guild.system_channel.send("Hello there, I'm a log bot. I'll be watching what you're doing. If you want to do something, you have to think twice.")


@bot.event
async def on_guild_remove(guild):
    print(guild.name)
    await bot.change_presence(activity=discord.Game(f"Log {len(bot.guilds)}"), status=discord.Status.online)


@bot.command(help=">>ping")
async def ping(ctx):
    await ctx.send(f"Pong! In **{round(bot.latency * 1000)}**ms")


@bot.command(help=">>status")
async def status(ctx):
    server = ctx.guild
    online = 0
    offline = 0
    dnd = 0
    idle = 0
    numberofmembers = 0
    numberofbot = 0
    numberoftextchannel = 0
    numberofvoicechannel = 0
    numberofvoiceconnect = 0
    for member in server.members:
        if member.bot:
            numberofbot += 1
        else:
            numberofmembers += 1
            if str(member.status) == "online":
                online += 1
            if str(member.status) == "offline":
                offline += 1
            if str(member.status) == "dnd":
                dnd += 1
            if str(member.status) == "idle":
                idle += 1
    for channel in server.text_channels:
        numberoftextchannel += 1
    for channel in server.voice_channels:
        numberofvoicechannel += 1
        if channel.members != []:
            numberofvoiceconnect += len(channel.members)

    message = f"🟢 {online} | ⛔ {dnd} | 🌙 {idle} | ◯ {offline} | 👤 {numberofmembers} | 🤖 {numberofbot} | 🗣 {numberofvoiceconnect} | 💬 {numberoftextchannel} | 🔊 {numberofvoicechannel}"
    await ctx.reply(message)


def GetTime(format=None):
    if format == None:
        format = "%d.%m.%Y - %H:%M:%S"
    fulltime = datetime.datetime.now(pytz.timezone("Europe/Istanbul"))
    fulltime = fulltime.strftime(format)
    return fulltime


async def getchannel(guild, category_name, channel_name):
    category = discord.utils.get(guild.categories, name=category_name)
    if category == None:
        await guild.create_category(category_name)
        category = discord.utils.get(guild.categories, name=category_name)
    channel = discord.utils.get(guild.text_channels, name=channel_name)
    if channel == None:
        await guild.create_text_channel(channel_name, category=category)
        channel = discord.utils.get(guild.text_channels, name=channel_name)
    return channel


@bot.event
async def on_member_join(member):
    channel = await getchannel(member.guild, "🗂 LOGS", "〖👋〗welcome")
    # await member.send('Private message')
    embed = discord.Embed()
    embed.color = discord.Colour.random()
    embed.set_author(icon_url=member.avatar_url, name=member, url=f"{member.avatar_url}")
    embed.set_footer(icon_url=member.guild.icon_url, text=f"{member.guild.name}   •   {GetTime()}")
    embed.description = f"**Hi {member.mention}, Welcome to {member.guild.name} server.**"
    await channel.send(embed=embed)
    if member.guild.system_channel is not None:
        await member.guild.system_channel.send(embed=embed)


@bot.event
async def on_member_remove(member):
    channel = await getchannel(member.guild, "🗂 LOGS", "〖🖕〗goodbye")
    # await member.send('Private message')
    embed = discord.Embed()
    embed.color = discord.Colour.random()
    embed.set_author(icon_url=member.avatar_url, name=member, url=f"{member.avatar_url}")
    embed.set_footer(icon_url=member.guild.icon_url, text=f"{member.guild.name}   •   {GetTime()}")
    embed.description = f"**Bye Bye {member.mention}. It was nice to be with you.**"
    await channel.send(embed=embed)
    if member.guild.system_channel is not None:
        await member.guild.system_channel.send(embed=embed)


@bot.event
async def on_voice_state_update(member, before, after):
    try:
        channel = await getchannel(member.guild, "🗂 LOGS", "〖🔊〗voice-channel-log")
        embed = discord.Embed()
        embed.color = discord.Colour.random()
        embed.set_author(icon_url=member.avatar_url, name=member, url=f"{member.avatar_url}")
        embed.set_footer(icon_url=member.guild.icon_url, text=f"{member.guild.name}   •   {GetTime()}")
        if before.channel is None and after.channel is not None:
            embed.description = f"**{member.mention} joined on {after.channel.mention} channel.**"
            await channel.send(embed=embed)
        if before.channel is not None and after.channel is None:
            embed.description = f"**{member.mention} left on {before.channel.mention} channel.**"
            await channel.send(embed=embed)
        if before.channel is not after.channel:
            embed.description = f"**{member.mention} switched between voice channels {before.channel.mention} => {after.channel.mention}**"
            await channel.send(embed=embed)
        if before.self_mute is False and after.self_mute is True:
            embed.description = f"**{member.mention}, muted itself on {before.channel.mention} channel.**"
            await channel.send(embed=embed)
        if before.self_mute is True and after.self_mute is False:
            embed.description = f"**{member.mention}, removed its muted on {before.channel.mention} channel.**"
            await channel.send(embed=embed)
        if before.self_deaf is False and after.self_deaf is True:
            embed.description = f"**{member.mention}, deafened itself on {before.channel.mention} channel.**"
            await channel.send(embed=embed)
        if before.self_deaf is True and after.self_deaf is False:
            embed.description = f"**{member.mention}, removed its deafness on {before.channel.mention} channel.**"
            await channel.send(embed=embed)
        if before.self_stream is False and after.self_stream is True:
            embed.description = f"**{member.mention}, shared its screen on {after.channel.mention} channel.**"
            await channel.send(embed=embed)
        if before.self_stream is True and after.self_stream is False:
            embed.description = f"**{member.mention}, turned off sharing its screen on {before.channel.mention} channel.**"
            await channel.send(embed=embed)
    except:
        pass


rolelastmessage = ""

@bot.event
async def on_member_update(before, after):
    global rolelastmessage
    if before.status != after.status:
        guild = before.guild
        channel = await getchannel(guild, "🗂 LOGS", "〖🌀〗status-log")
        embed = discord.Embed()
        embed.color = discord.Colour.random()
        embed.set_author(icon_url=after.avatar_url, name=after, url=f"{after.avatar_url}")
        embed.set_footer(icon_url=guild.icon_url, text=f"{guild.name}   •   {GetTime()}")
        message = f"**{after.mention}, changed its presence {before.status} => {after.status}**"
        if message.count("idle") == 2 or message.count("offline") == 2 or message.count("online") == 2 or message.count("dnd") == 2:
            return
        message = message.replace("idle", "🌙")
        message = message.replace("online", "🟢")
        message = message.replace("offline", "◯")
        message = message.replace("dnd", "⛔")
        embed.description = message
        await channel.send(embed=embed)

    if before.roles != after.roles:
        channel = await getchannel(before.guild, "🗂 LOGS", "〖🎅🏿〗role-log")
        embed = discord.Embed()
        embed.color = discord.Colour.random()
        embed.set_author(icon_url=after.avatar_url, name=after, url=f"{after.avatar_url}")
        embed.set_footer(icon_url=after.guild.icon_url, text=f"{after.guild.name}   •   {GetTime()}")
        embed.description = f"**Roles of {after.mention} updated.**"
        beforeroles = ""
        for x in before.roles:
            beforeroles += f"{x.mention}\n"
        afterroles = ""
        for x in after.roles:
            afterroles += f"{x.mention}\n"
        embed.add_field(name="↓Before Roles↓", value=beforeroles, inline=True)
        embed.add_field(name="↓After Roles↓", value=afterroles, inline=True)
        message = f"{beforeroles} + {afterroles}"
        if message != rolelastmessage and message != "":
            rolelastmessage = message
            await channel.send(embed=embed)

    if before.activity != after.activity:
        try:
            activity_type = after.activity.type
        except:
            activity_type = before.activity.type
        if activity_type == discord.ActivityType.listening:
            guild = after.guild
            channel = await getchannel(guild, "🗂 LOGS", "〖🎧〗spotify-log")
            embed = discord.Embed()
            embed.color = discord.Colour.random()
            embed.set_author(icon_url=after.avatar_url, name=after, url=f"{after.avatar_url}")
            embed.set_footer(icon_url=guild.icon_url, text=f"{guild.name}   •   {GetTime()}")

            if str(before.activity) == "Spotify" and str(after.activity) == "Spotify":
                message = f"**{after.name}**, changed the song: **{before.activities[0].title}** by ***{before.activities[0].artist}*** >>> **{after.activities[0].title}** by ***{after.activities[0].artist}***"
                embed.description = f"**{after.mention}, changed the song.**"
                beforesong = f"{before.activities[0].title} by {before.activities[0].artist}"
                aftersong = f"{after.activities[0].title} by {after.activities[0].artist}"
                if beforesong == aftersong:
                    return
                embed.add_field(name="Previous Song:", value=f"```{before.activities[0].title} by {before.activities[0].artist}```", inline=False)
                embed.add_field(name="Next Song:", value=f"```{after.activities[0].title} by {after.activities[0].artist}```", inline=False)
            if str(before.activity) == "None" and str(after.activity) == "Spotify":
                message = f"**{after.name}**, started listening to Spotify: **{after.activities[0].title}** by ***{after.activities[0].artist}***"
                embed.description = f"**{after.mention}, started listening to Spotify.**"
                embed.add_field(name="Song:", value=f"```{after.activities[0].title} by {after.activities[0].artist}```", inline=False)
            if str(before.activity) == "Spotify" and str(after.activity) == "None":
                message = f"**{after.name}**, stopped listening to Spotify: **{before.activities[0].title}** by ***{before.activities[0].artist}***"
                embed.description = f"**{after.mention}, stopped listening to Spotify.**"
                embed.add_field(name="Song:", value=f"```{before.activities[0].title} by {before.activities[0].artist}```", inline=False)
            await channel.send(embed=embed)
        elif activity_type == discord.ActivityType.playing:
            pass


@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    channel = await getchannel(message.guild, "🗂 LOGS", "〖📃〗message-delete")
    embed = discord.Embed()
    embed.color = discord.Colour.random()
    embed.set_author(icon_url=message.author.avatar_url, name=message.author, url=f"{message.author.avatar_url}")
    embed.set_footer(icon_url=message.author.guild.icon_url, text=f"{message.author.guild.name}   •   {GetTime()}")
    embed.description = f"**Message sent by {message.author.mention}, deleted on {message.channel.mention} channel.**"
    embed.add_field(name="Message:", value=f"```{message.content}```", inline=False)
    await channel.send(embed=embed)


@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    if before.content == after.content:
        return
    channel = await getchannel(before.guild, "🗂 LOGS", "〖📝〗message-edit")
    embed = discord.Embed()
    embed.color = discord.Colour.random()
    embed.set_author(icon_url=before.author.avatar_url, name=before.author, url=f"{before.author.avatar_url}")
    embed.set_footer(icon_url=before.author.guild.icon_url, text=f"{before.author.guild.name}   •   {GetTime()}")
    embed.description = f"**Message sent by {before.author.mention}, updated on {after.channel.mention} channel.**"
    embed.add_field(name="Old Message:", value=f"```{before.content}```", inline=False)
    embed.add_field(name="New Message:", value=f"```{after.content}```", inline=False)
    await channel.send(embed=embed)


@bot.event
async def on_typing(channel, user, when):
    if user.bot:
        return
    sendchannel = await getchannel(user.guild, "🗂 LOGS", "〖⌨〗typing-log")
    embed = discord.Embed()
    embed.color = discord.Colour.random()
    embed.set_author(icon_url=user.avatar_url, name=user, url=f"{user.avatar_url}")
    embed.set_footer(icon_url=user.guild.icon_url, text=f"{user.guild.name}   •   {GetTime()}")
    embed.description = f"**{user.mention} was seen typing on {channel.mention} channel.**"
    await sendchannel.send(embed=embed)


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot == False:
        channel = await getchannel(user.guild, "🗂 LOGS", "〖💥〗reaction-log")
        embed = discord.Embed()
        embed.color = discord.Colour.random()
        embed.set_author(icon_url=user.avatar_url, name=user, url=f"{user.avatar_url}")
        embed.description = f"**{user.mention} left {reaction} reaction to a message.**"
        embed.add_field(name="Message:", value=f"```{reaction.message.content}```", inline=False)
        embed.add_field(name="Author", value=f"{reaction.message.author.mention}", inline=True)
        embed.add_field(name="Channel:", value=f"{reaction.message.channel.mention}", inline=True)
        embed.set_footer(icon_url=user.guild.icon_url, text=f"{user.guild.name}   •   {GetTime()}")
        await channel.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    print(error)


keep_alive()
bot.run("token")
