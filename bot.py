import os
import traceback
import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import View, Button, Modal, TextInput
import aiohttp
import asyncio
import random
import json
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

bot.remove_command('help')
CUTE_REPLIES = ["Hewwo! 🥰", "Yes? 💖", "I'm here! ✨", "What's up, cutie? 🌸", "Hi hi! 🎀", "Listening! 💕"]
DAILY_QUOTES = ["You are all so beautiful! Remember to drink water today! 💖🥰", "Sending virtual hugs to everyone in CutieWorld! 🌸✨", "Smile! You look so cute when you smile! 🥺💖", "CutieWorld is lucky to have such amazing members! 🎀💕", "Take a deep breath, everything is going to be okay! 🌸✨"]

def get_channel(guild, name):
    for c in guild.text_channels:
        if c.name == name: return c
    return None

def get_category(guild, name):
    for c in guild.categories:
        if c.name == name: return c
    return None

class TicketView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Open Ticket", emoji="🎟️", style=discord.ButtonStyle.green, custom_id="open_ticket_btn")
    async def ticket_btn(self, interaction: discord.Interaction, button: Button):
        cat = get_category(interaction.guild, "･ﾟ･｡ support")
        if not cat: return
        member = await interaction.guild.fetch_member(interaction.user.id)
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False), member: discord.PermissionOverwrite(view_channel=True, send_messages=True)}
        chan = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", category=cat, overwrites=overwrites)
        await chan.send(f"Hey {interaction.user.mention}! Staff will be here soon.", view=CloseTicketView())
        await interaction.response.send_message(f"Ticket created: {chan.mention}", ephemeral=True)

class PartnerTicketView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Partner Request", emoji="🤝", style=discord.ButtonStyle.blurple, custom_id="partner_ticket_btn")
    async def partner_ticket_btn(self, interaction: discord.Interaction, button: Button):
        cat = get_category(interaction.guild, "･ﾟ･｡ support")
        if not cat: return
        member = await interaction.guild.fetch_member(interaction.user.id)
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False), member: discord.PermissionOverwrite(view_channel=True, send_messages=True)}
        chan = await interaction.guild.create_text_channel(f"partner-{interaction.user.name}", category=cat, overwrites=overwrites)
        await chan.send(f"Hey {interaction.user.mention}! Please provide your server name, invite link, and member count.", view=CloseTicketView())
        await interaction.response.send_message(f"Partner ticket created: {chan.mention}", ephemeral=True)

class CloseTicketView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Close Ticket", emoji="🔒", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Closing...", ephemeral=True)
        await asyncio.sleep(3)
        await interaction.channel.delete()

class RoleView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Under 13", style=discord.ButtonStyle.red, custom_id="role_under13")
    async def r_u13(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="👶 Under 13")
        if role: await interaction.user.add_roles(role)
        await interaction.response.send_message("Role added!", ephemeral=True)
    @discord.ui.button(label="13-17", style=discord.ButtonStyle.blurple, custom_id="role_13_17")
    async def r_1317(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="🌸 13-17")
        if role: await interaction.user.add_roles(role)
        await interaction.response.send_message("Role added!", ephemeral=True)
    @discord.ui.button(label="18+", style=discord.ButtonStyle.green, custom_id="role_18_plus")
    async def r_18(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="🌸 18+")
        if role: await interaction.user.add_roles(role)
        await interaction.response.send_message("Role added!", ephemeral=True)
    @discord.ui.button(label="She/Her", style=discord.ButtonStyle.red, custom_id="role_sheher")
    async def r_she(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="♀️ She/Her")
        if role: await interaction.user.add_roles(role)
        await interaction.response.send_message("Role added!", ephemeral=True)
    @discord.ui.button(label="He/Him", style=discord.ButtonStyle.blurple, custom_id="role_hehim")
    async def r_he(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="♂️ He/Him")
        if role: await interaction.user.add_roles(role)
        await interaction.response.send_message("Role added!", ephemeral=True)
    @discord.ui.button(label="They/Them", style=discord.ButtonStyle.green, custom_id="role_theythem")
    async def r_they(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="🏳️‍🌈 They/Them")
        if role: await interaction.user.add_roles(role)
        await interaction.response.send_message("Role added!", ephemeral=True)

class BestieModal(Modal, title="Find Your Bestie 💖"):
    vibe = TextInput(label="What is your vibe?", placeholder="e.g. Soft girl, edgy, sleepy", style=discord.TextStyle.short)
    color = TextInput(label="Favorite color?", placeholder="e.g. Pink, Black, Blue", style=discord.TextStyle.short)
    def __init__(self): super().__init__()
    async def on_submit(self, interaction: discord.Interaction):
        data = load_data()
        gid = str(interaction.guild.id)
        uid = str(interaction.user.id)
        if gid not in data: data[gid] = {}
        data[gid][uid] = {"vibe": self.vibe.value.lower(), "color": self.color.value.lower(), "match": None}
        save_data(data)
        await interaction.response.send_message("Profile saved! Looking for a match... 🎀", ephemeral=True)
        await check_match(interaction.user, interaction.guild)

def load_data():
    if not os.path.exists("cutieworld_data.json"): return {}
    with open("cutieworld_data.json", 'r', encoding='utf-8') as f: return json.load(f)

def save_data(data):
    with open("cutieworld_data.json", 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)

async def check_match(user, guild):
    data = load_data()
    gid = str(guild.id)
    uid = str(user.id)
    if gid not in data: return
    my_profile = data[gid].get(uid)
    if not my_profile or my_profile.get("match"): return
    
    for target_id, profile in data[gid].items():
        if target_id == uid or profile.get("match"): continue
        if profile["vibe"] == my_profile["vibe"] or profile["color"] == my_profile["color"]:
            target = guild.get_member(int(target_id))
            if not target: continue
            
            cat = get_category(guild, "♡ introductions")
            if not cat: return
            overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False), user: discord.PermissionOverwrite(view_channel=True, send_messages=True), target: discord.PermissionOverwrite(view_channel=True, send_messages=True)}
            chan = await guild.create_text_channel(f"bestie-{user.name}-{target.name}", category=cat, overwrites=overwrites)
            
            await chan.send(f"🎀 **Match Found!** 🎀\n{user.mention} and {target.mention} you are perfect besties!\nTalk and get to know each other! 💖")
            
            data[gid][uid]["match"] = target_id
            data[gid][target_id]["match"] = uid
            save_data(data)
            return

@bot.event
async def on_ready():
    bot.add_view(TicketView())
    bot.add_view(PartnerTicketView())
    bot.add_view(CloseTicketView())
    bot.add_view(RoleView())
    await tree.sync()
    print(f'CutiePie online: {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="CutieWorld 💖"))
    if not daily_quote.is_running(): daily_quote.start()
    if not vanity_sniper_task.is_running(): vanity_sniper_task.start()

async def send_welcome(member):
    try:
        ch = get_channel(member.guild, "♡ welcome")
        if ch:
            embed = discord.Embed(title="Welcome to CutieWorld! 🌸", description=f"Hey {member.mention}! We are so happy to have you here! 🥰\n\n**Step 1:** Go to the **♡ verify** channel.\n**Step 2:** Type `/verify` and hit enter.\n**Step 3:** Enjoy the server!", color=discord.Color.pink())
            embed.set_thumbnail(url=member.display_avatar.url)
            await ch.send(embed=embed)
    except Exception as e: print(f"Welcome Error: {e}")

@bot.event
async def on_member_join(member):
    await send_welcome(member)
    if discord.utils.get(member.guild.roles, name="🔒 LOCKDOWN"):
        try: await member.edit(roles=[])
        except: pass

@bot.event
async def on_raw_member_add(payload):
    try:
        guild = bot.get_guild(payload.guild_id)
        if not guild: return
        member = await guild.fetch_member(payload.user.id)
        if not member.joined_at or (discord.utils.utcnow() - member.joined_at).total_seconds() < 10:
            await send_welcome(member)
    except Exception as e: print(f"Raw Welcome Error: {e}")

@bot.event
async def on_message(message):
    if message.author.bot: return
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound): return
    print(f"Error: {error}")

@tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    print(f"App Error: {error}")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.bot: return
    if str(payload.emoji.name) == "💎":
        ch = bot.get_channel(payload.channel_id)
        if ch and ch.name == "boost-log":
            await ch.send(f"🎉 {payload.member.mention} just boosted CutieWorld! Thank you so much! 💖✨")
            await ch.remove_reaction(payload.emoji, payload.member)

@tasks.loop(hours=24)
async def daily_quote():
    for guild in bot.guilds:
        ch = get_channel(guild, "♡ chat")
        if ch: await ch.send(random.choice(DAILY_QUOTES))

@tasks.loop(minutes=5)
async def vanity_sniper_task():
    if not bot.guilds: return
    guild = bot.guilds[0]
    if not guild.features: return
    ch = get_channel(guild, "💎 booster-exclusive")
    if not ch: return
    target_word = "cutie"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://discord.com/api/v10/invites/{target_word}") as resp:
                if resp.status == 404:
                    for owner in [m for m in guild.members if m.guild_permissions.administrator]:
                        await owner.send(f"🚨 **VANITY URL AVAILABLE!** 🚨\n`discord.gg/{target_word}` is unclaimed right now! GO GRAB IT!")
    except: pass

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="💖 CutiePie Help 🌸", description="Here are all my cute commands!", color=discord.Color.pink())
    embed.add_field(name="✨ Verification", value="`/verify`", inline=False)
    embed.add_field(name="🎀 Cute Actions", value="`/hug` `/kiss` `/pat` `/cuddle` `/blush` `/slap` `/hold` `/poke` `/tickle` `/wave` `/highfive` `/pinch`", inline=False)
    embed.add_field(name="🎲 Fun & Games", value="`/8ball` `/roll` `/coinflip` `/truth` `/dare` `/rate` `/pick`", inline=False)
    embed.add_field(name="📈 Leveling", value="`/rank`", inline=False)
    embed.add_field(name="🎀 Bestie Finder", value="`/bestie`", inline=False)
    embed.add_field(name="🕵️ Stealth Tools", value="`/steal` `/sniper`", inline=False)
    embed.add_field(name="🔍 Utilities", value="`/avatar` `/userinfo` `/serverinfo` `/define`", inline=False)
    embed.add_field(name="🛡️ Admin", value="`/setup` `/lockdown` `/unlock` `/mute` `/unmute` `/purge` `/ban` `/kick`", inline=False)
    embed.add_field(name="👑 Community", value="`/fame` `/expose` `/suggest` `/giveaway`", inline=False)
    await ctx.send(embed=embed)

@tree.command(name="verify")
async def verify(interaction: discord.Interaction):
    try:
        member = await interaction.guild.fetch_member(interaction.user.id)
        cutie_role = discord.utils.get(interaction.guild.roles, name="✨ Cuties")
        member_role = discord.utils.get(interaction.guild.roles, name="♡ Member")
        if not cutie_role or not member_role: return await interaction.response.send_message("Roles are missing. Ask an admin to run /setup.", ephemeral=True)
        await member.add_roles(cutie_role, member_role, reason="Verified")
        verify_ch = get_channel(interaction.guild, "♡ verify")
        if verify_ch: await verify_ch.set_permissions(member, view_channel=False, send_messages=False)
        await interaction.response.send_message("Verified! Welcome to CutieWorld! 🌸", ephemeral=True)
    except Exception as e: print(f"Verify Error: {e}")

@tree.command(name="bestie")
async def bestie(interaction: discord.Interaction):
    await interaction.response.send_modal(BestieModal())

@tree.command(name="steal", description="(Admin) Steal content from another server")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(link="Discord invite link")
async def steal(interaction: discord.Interaction, link: str):
    await interaction.response.send_message("Joining target server... this takes about 10 seconds. Please wait.", ephemeral=True)
    try:
        code = link.split("/")[-1].split(" ")[0]
        await bot.join_invite(code)
        await asyncio.sleep(8)
        
        target_guild = None
        for g in bot.guilds:
            if g.id != interaction.guild.id:
                target_guild = g
                break
                
        if not target_guild: return await interaction.followup.send("Failed to find target server.", ephemeral=True)
        
        stolen_count = 0
        for channel in target_guild.text_channels:
            if not channel.permissions_for(target_guild.me).read_message_history: continue
            try:
                async for msg in channel.history(limit=20):
                    if msg.attachments:
                        for a in msg.attachments:
                            if a.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4')):
                                embed = discord.Embed(description=f"**Stolen from {target_guild.name}** 🤫", color=discord.Color.pink())
                                embed.set_image(url=a.url)
                                ch_media = get_channel(interaction.guild, "꩜ memes")
                                if ch_media: 
                                    await ch_media.send(embed=embed)
                                    stolen_count += 1
                                    if stolen_count >= 5: break
            except: pass
            if stolen_count >= 5: break
            
        await target_guild.leave()
        await interaction.followup.send(f"Stole {stolen_count} images! Left the target server.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Error: {e}", ephemeral=True)

@tree.command(name="sniper", description="See sniper status")
async def sniper(interaction: discord.Interaction):
    embed = discord.Embed(title="🎯 Vanity Sniper", description=f"Currently watching: `discord.gg/cutie`\nChecks every 5 minutes.", color=discord.Color.pink())
    await interaction.response.send_message(embed=embed)

@tree.command(name="setup")
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id: return await interaction.response.send_message("Owner only.", ephemeral=True)
    await interaction.response.send_message("⚠️ **Nuking everything and rebuilding CutieWorld...**", ephemeral=True)
    for channel in interaction.guild.channels:
        try: await channel.delete()
        except: pass
    for category in interaction.guild.categories:
        try: await category.delete()
        except: pass

    await interaction.guild.create_role(name="✨ Cuties", color=discord.Color.pink())
    await interaction.guild.create_role(name="♡ Member", color=discord.Color.from_rgb(255, 192, 203))
    await interaction.guild.create_role(name="💎 Boosters", color=discord.Color.purple())
    await interaction.guild.create_role(name="🛡️ Security", color=discord.Color.red())
    await interaction.guild.create_role(name="🤝 Partners", color=discord.Color.teal())
    await interaction.guild.create_role(name="⚠️ Muted", color=discord.Color.dark_gray())
    await interaction.guild.create_role(name="👶 Under 13", color=discord.Color.light_grey())
    await interaction.guild.create_role(name="🌸 13-17", color=discord.Color.pink())
    await interaction.guild.create_role(name="🌸 18+", color=discord.Color.dark_magenta())
    await interaction.guild.create_role(name="♀️ She/Her", color=discord.Color.pink())
    await interaction.guild.create_role(name="♂️ He/Him", color=discord.Color.blue())
    await interaction.guild.create_role(name="🏳️‍🌈 They/Them", color=discord.Color.default())

    verified = discord.utils.get(interaction.guild.roles, name="✨ Cuties")
    default_hide = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False)}
    verified_show = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False), verified: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)}
    read_only = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False), verified: discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True)}

    c1 = await interaction.guild.create_category("･ﾟ･｡ welcome", overwrites={interaction.guild.default_role: discord.PermissionOverwrite(view_channel=True, read_message_history=True)})
    await asyncio.sleep(1)
    await c1.create_text_channel("♡ welcome", overwrites={interaction.guild.default_role: discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=False)})
    await asyncio.sleep(0.5)
    await c1.create_text_channel("๑ rules", overwrites={interaction.guild.default_role: discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=False)})
    await asyncio.sleep(0.5)
    ch_verify = await c1.create_text_channel("♡ verify", overwrites={interaction.guild.default_role: discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=True, use_application_commands=True)})
    await ch_verify.send("Type `/verify` to get your cute roles and enter the server! 🌸")
    await asyncio.sleep(0.5)
    
    c_intros = await interaction.guild.create_category("♡ introductions", overwrites=verified_show)
    await asyncio.sleep(1)
    ch_intro = await c_intros.create_text_channel("♡ intros")
    await ch_intro.send("```Tell us about yourself!\nName:\nAge:\nInterests:\nFavorite color:```\n**Click the buttons below to get your age and pronoun roles!**", view=RoleView())
    await asyncio.sleep(0.5)
    await c_intros.create_text_channel("♡ departures")

    c2 = await interaction.guild.create_category("♡ main chat", overwrites=verified_show)
    await asyncio.sleep(1)
    await c2.create_text_channel("♡ chat")
    await asyncio.sleep(0.5)
    ch_bots = await c2.create_text_channel("๑ bot-commands")
    await ch_bots.send("```✨ do !help for assistance ✨```")
    await asyncio.sleep(0.5)
    await c2.create_text_channel("๑ spam")
    await asyncio.sleep(0.5)
    v1 = await c2.create_voice_channel("♡ Lounge"); await v1.edit(user_limit=10)
    await asyncio.sleep(0.5)
    v2 = await c2.create_voice_channel("♡ Private 1"); await v2.edit(user_limit=3)

    c3 = await interaction.guild.create_category("꩜ media", overwrites=verified_show)
    await asyncio.sleep(1)
    ch_selfies = await c3.create_text_channel("꩜ selfies")
    await ch_selfies.send(embed=discord.Embed(title="📸 Selfies Rules", description="Only **pictures and videos** allowed here!\nNo GIFs, no text, just your cute faces! 🥰", color=discord.Color.pink()))
    await asyncio.sleep(0.5)
    ch_face = await c3.create_text_channel("꩜ face-reveal")
    await ch_face.send(embed=discord.Embed(title="🌸 Face Reveal Rules", description="Only **pictures and videos** allowed here!\nBe brave! No GIFs. 🌸", color=discord.Color.pink()))
    await asyncio.sleep(0.5)
    ch_memes = await c3.create_text_channel("꩜ memes")
    await ch_memes.send(embed=discord.Embed(title="😂 Memes Rules", description="Post your funniest **GIFs, videos, and pictures**!\nKeep it SFW. 💖", color=discord.Color.pink()))
    await asyncio.sleep(0.5)
    ch_aesth = await c3.create_text_channel("꩜ aesthetics")
    await ch_aesth.send(embed=discord.Embed(title="🎨 Aesthetics Rules", description="Only **pictures** allowed here!\nNo GIFs, no videos, strictly aesthetic photos. ✨", color=discord.Color.pink()))
    await asyncio.sleep(0.5)
    ch_clips = await c3.create_text_channel("꩜ gaming-clips")
    await ch_clips.send(embed=discord.Embed(title="🎮 Gaming Clips Rules", description="Post your **videos and links** (YouTube/Twitch) here!\nNo raw pictures or GIFs. 🎯", color=discord.Color.pink()))

    c4 = await interaction.guild.create_category("彡 community", overwrites=read_only)
    await asyncio.sleep(1)
    ch_fame = await c4.create_text_channel("彡 hall-of-fame")
    await ch_fame.send("👑 **Hall of Fame**\nBest of the best get posted here.")
    await asyncio.sleep(0.5)
    ch_lose = await c4.create_text_channel("彡 loser-hall-of-fame")
    await ch_lose.send("🤡 **Loser Hall of Fame**\nExposing people who did stupid shit. Use `/expose` to add someone!")
    await asyncio.sleep(0.5)
    await c4.create_text_channel("彡 polls")
    vm = await c4.create_voice_channel("彡 Music"); await vm.edit(user_limit=5)

    c_sugg = await interaction.guild.create_category("彡 suggestions", overwrites=verified_show)
    await asyncio.sleep(1)
    await c_sugg.create_text_channel("彡 server-suggestions")

    c5 = await interaction.guild.create_category("🤝 partnerships", overwrites=read_only)
    await asyncio.sleep(1)
    await c5.create_text_channel("🤝 partners")
    await asyncio.sleep(0.5)
    ch_how = await c5.create_text_channel("🤝 how-to-partner")
    await ch_how.send(embed=discord.Embed(title="🤝 How To Partner", description="Want to partner with CutieWorld? It's super easy!\n\n**Step 1:** Click the purple **'Partner Request'** button right below this message.\n**Step 2:** A private chat will open just for you and the staff.\n**Step 3:** Send your Server Name, Invite Link, and Member Count in that chat.\n**Step 4:** We will look at it and add you if it's a good fit! 💖", color=discord.Color.teal()), view=PartnerTicketView())
    await asyncio.sleep(0.5)
    await c5.create_text_channel("🤝 partner-logs")

    c6 = await interaction.guild.create_category("💎 boosters", overwrites=read_only)
    await asyncio.sleep(1)
    await c6.create_text_channel("💎 boost-chat")
    await asyncio.sleep(0.5)
    ch_blog = await c6.create_text_channel("💎 boost-log")
    await ch_blog.send("React with 💎 in here when you boost to get logged!")
    await asyncio.sleep(0.5)
    await c6.create_text_channel("💎 booster-exclusive")
    vb = await c6.create_voice_channel("💎 Booster Lounge"); await vb.edit(user_limit=5)

    c7 = await interaction.guild.create_category("･ﾟ･｡ support", overwrites=default_hide)
    await asyncio.sleep(1)
    ch_t = await c7.create_text_channel("open-ticket")
    await ch_t.send("Need help? Open a ticket below.", view=TicketView())

    try: await interaction.edit_original_response(content="✅ **CutieWorld perfectly rebuilt. 🌸✨")
    except: pass

# --- SECURITY ---
@tree.command(name="lockdown")
@app_commands.checks.has_permissions(administrator=True)
async def lockdown(interaction: discord.Interaction):
    await interaction.guild.create_role(name="🔒 LOCKDOWN", color=discord.Color.red())
    for r in interaction.guild.roles:
        try: await r.edit(send_messages=False)
        except: pass
    await interaction.response.send_message("🚨 **LOCKDOWN INITIATED** 🚨", ephemeral=True)

@tree.command(name="unlock")
@app_commands.checks.has_permissions(administrator=True)
async def unlock(interaction: discord.Interaction):
    role = discord.utils.get(interaction.guild.roles, name="🔒 LOCKDOWN")
    if role: await role.delete()
    for r in interaction.guild.roles:
        try: await r.edit(send_messages=None)
        except: pass
    await interaction.response.send_message("✅ Unlocked.", ephemeral=True)

@tree.command(name="mute")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute_cmd(interaction: discord.Interaction, user: discord.Member):
    role = discord.utils.get(interaction.guild.roles, name="⚠️ Muted")
    if role: await user.add_roles(role)
    await interaction.response.send_message(f"Muted {user.name}.", ephemeral=True)

@tree.command(name="unmute")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute_cmd(interaction: discord.Interaction, user: discord.Member):
    role = discord.utils.get(interaction.guild.roles, name="⚠️ Muted")
    if role: await user.remove_roles(role)
    await interaction.response.send_message(f"Unmuted {user.name}.", ephemeral=True)

@tree.command(name="purge")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(amount="Amount to delete")
async def purge(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount + 1)
    await interaction.response.send_message("Nuked.", ephemeral=True)

@tree.command(name="ban")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member):
    await user.ban()
    await interaction.response.send_message(f"Banned {user.name}.", ephemeral=True)

@tree.command(name="kick")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member):
    await user.kick()
    await interaction.response.send_message(f"Kicked {user.name}.", ephemeral=True)

# --- COMMUNITY ---
@tree.command(name="fame")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(user="Target", reason="Why")
async def fame(interaction: discord.Interaction, user: discord.Member, reason: str):
    ch = get_channel(interaction.guild, "彡 hall-of-fame")
    if ch:
        embed = discord.Embed(title="👑 Hall of Fame!", description=f"**{user.mention}** has made it!\n**Reason:** {reason}", color=discord.Color.gold())
        embed.set_thumbnail(url=user.display_avatar.url)
        await ch.send(embed=embed)
    await interaction.response.send_message("Added.", ephemeral=True)

@tree.command(name="expose")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(user="Target", reason="Why")
async def expose(interaction: discord.Interaction, user: discord.Member, reason: str):
    ch = get_channel(interaction.guild, "彡 loser-hall-of-fame")
    if ch:
        embed = discord.Embed(title="🤡 Exposed!", description=f"**{user.mention}** is a loser!\n**Reason:** {reason}", color=discord.Color.red())
        embed.set_thumbnail(url=user.display_avatar.url)
        await ch.send(embed=embed)
    await interaction.response.send_message("Exposed.", ephemeral=True)

@tree.command(name="suggest")
@app_commands.describe(suggestion="Your idea")
async def suggest(interaction: discord.Interaction, suggestion: str):
    ch = get_channel(interaction.guild, "彡 server-suggestions")
    if ch:
        embed = discord.Embed(title="💡 New Suggestion", description=f"**{interaction.user.mention}** suggests:\n\n{suggestion}", color=discord.Color.pink())
        msg = await ch.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
    await interaction.response.send_message("Suggestion posted!", ephemeral=True)

@tree.command(name="giveaway")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(time="Minutes", prize="Prize")
async def giveaway(interaction: discord.Interaction, time: int, prize: str):
    await interaction.response.send_message(f"🎉 **Giveaway started!** React with 🎉 to win **{prize}**! Ends in {time} minutes.")
    msg = await interaction.original_response()
    await msg.add_reaction("🎉")
    await asyncio.sleep(time * 60)
    users = [u async for u in msg.reactions[0].users() if not u.bot]
    if users:
        winner = random.choice(users)
        await interaction.followup.send(f"🎊 **Congratulations {winner.mention}! You won the {prize}!** 🎊")
    else:
        await interaction.followup.send("Nobody entered.")

@tree.command(name="rank")
async def rank(interaction: discord.Interaction):
    days = (datetime.utcnow() - interaction.user.joined_at).days
    level = days // 7
    xp = (days % 7) * 14
    bar_filled = int((xp / 100) * 10)
    bar = "🩷" * bar_filled + "🤍" * (10 - bar_filled)
    embed = discord.Embed(title=f"📈 {interaction.user.name}'s Rank", description=f"**Level {level}**\n[{bar}] {xp}/100 XP\n*(XP is based on how long you've been in CutieWorld!)*", color=discord.Color.pink())
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# --- FUN ---
@tree.command(name="8ball")
@app_commands.describe(question="Question")
async def eightball(interaction: discord.Interaction, question: str):
    responses = ["It is certain 💖", "Without a doubt ✨", "Yes definitely 🥰", "Reply hazy try again 🤔", "Ask again later 🌸", "Don't count on it 😔", "My reply is no 💔", "Very doubtful 🚫"]
    embed = discord.Embed(title="🔮 Magic 8 Ball", description=f"**Q:** {question}\n**A:** {random.choice(responses)}", color=discord.Color.pink())
    await interaction.response.send_message(embed=embed)

@tree.command(name="roll")
@app_commands.describe(sides="Sides")
async def roll(interaction: discord.Interaction, sides: int = 6):
    embed = discord.Embed(title="🎲 Dice Roll", description=f"You rolled a **{random.randint(1, sides)}**!", color=discord.Color.pink())
    await interaction.response.send_message(embed=embed)

@tree.command(name="coinflip")
async def coinflip(interaction: discord.Interaction):
    embed = discord.Embed(title="🪙 Coin Flip", description=f"It's **{random.choice(['Heads', 'Tails'])}**!", color=discord.Color.pink())
    await interaction.response.send_message(embed=embed)

@tree.command(name="truth")
async def truth(interaction: discord.Interaction):
    truths = ["What is your biggest secret? 🤫", "Who was your last crush? 😳", "Most embarrassing moment? 🙈", "Deepest fear? 😨", "Lied to get out of plans? 🤥"]
    embed = discord.Embed(title="🤫 Truth!", description=random.choice(truths), color=discord.Color.pink())
    await interaction.response.send_message(embed=embed)

@tree.command(name="dare")
async def dare(interaction: discord.Interaction):
    dares = ["Send your last saved photo! 📸", "Let someone ping whoever they want for 5 mins! 📢", "Impression of a baby! 👶", "Only emojis for 3 messages! 😀", "Compliment the person above you! 💖"]
    embed = discord.Embed(title="大胆 Dare!", description=random.choice(dares), color=discord.Color.pink())
    await interaction.response.send_message(embed=embed)

@tree.command(name="rate")
@app_commands.describe(thing="What to rate")
async def rate(interaction: discord.Interaction, thing: str):
    embed = discord.Embed(title="⭐ Rating", description=f"I rate **{thing}** a **{random.randint(1, 10)}/10**!", color=discord.Color.pink())
    await interaction.response.send_message(embed=embed)

@tree.command(name="pick")
@app_commands.describe(options="Opt 1, Opt 2")
async def pick(interaction: discord.Interaction, options: str):
    choices = [x.strip() for x in options.split(',')]
    if len(choices) < 2: return await interaction.response.send_message("Give me at least 2 options!", ephemeral=True)
    embed = discord.Embed(title="🤔 I pick...", description=f"**{random.choice(choices)}**!", color=discord.Color.pink())
    await interaction.response.send_message(embed=embed)

# --- CUTE ACTIONS ---
@tree.command(name="hug")
async def hug(interaction: discord.Interaction, user: discord.Member): await interaction.response.send_message(f"🥰 **{interaction.user.mention} gives {user.mention} a big warm hug!** 💖")
@tree.command(name="kiss")
async def kiss(interaction: discord.Interaction, user: discord.Member): await interaction.response.send_message(f"😘 **{interaction.user.mention} kisses {user.mention}!** 💕")
@tree.command(name="pat")
async def pat(interaction: discord.Interaction, user: discord.Member): await interaction.response.send_message(f"✨ **{interaction.user.mention} pats {user.mention}'s head** 🥺")
@tree.command(name="cuddle")
async def cuddle(interaction: discord.Interaction, user: discord.Member): await interaction.response.send_message(f"🎀 **{interaction.user.mention} cuddles {user.mention}** 🥰")
@tree.command(name="blush")
async def blush(interaction: discord.Interaction): await interaction.response.send_message(f"🥺👀💖 **{interaction.user.name} covers their face**")
@tree.command(name="slap")
async def slap(interaction: discord.Interaction, user: discord.Member): await interaction.response.send_message(f"🤚 **{interaction.user.mention} slaps {user.mention}!** 🤡")
@tree.command(name="hold")
async def hold(interaction: discord.Interaction, user: discord.Member): await interaction.response.send_message(f"🫂 **{interaction.user.mention} holds {user.mention}'s hand** 💕")
@tree.command(name="poke")
async def poke(interaction: discord.Interaction, user: discord.Member): await interaction.response.send_message(f"👉 **{interaction.user.mention} pokes {user.mention}** 🥺")
@tree.command(name="tickle")
async def tickle(interaction: discord.Interaction, user: discord.Member): await interaction.response.send_message(f"🪶 **{interaction.user.mention} tickles {user.mention}!** 😂")
@tree.command(name="wave")
async def wave(interaction: discord.Interaction, user: discord.Member): await interaction.response.send_message(f"👋 **{interaction.user.mention} waves at {user.mention}!** ✨")
@tree.command(name="highfive")
async def highfive(interaction: discord.Interaction, user: discord.Member): await interaction.response.send_message(f"✋ **{interaction.user.mention} gives {user.mention} a high five!** 🌟")
@tree.command(name="pinch")
async def pinch(interaction: discord.Interaction, user: discord.Member): await interaction.response.send_message(f"🤏 **{interaction.user.mention} pinches {user.mention}'s cheek!** 🥰")

# --- UTILITIES ---
@tree.command(name="define")
@app_commands.describe(word="Word")
async def define(interaction: discord.Interaction, word: str):
    await interaction.response.defer()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}") as resp:
            if resp.status == 200:
                data = await resp.json()
                defn = data[0]["meanings"][0]["definitions"][0]["definition"]
                embed = discord.Embed(title=f"📖 {word.capitalize()}", description=defn, color=discord.Color.pink())
            else: embed = discord.Embed(title="Error", description="Word not found.", color=discord.Color.red())
    await interaction.followup.send(embed=embed)

@tree.command(name="avatar")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"{user.name}'s Avatar", color=discord.Color.pink()).set_image(url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@tree.command(name="userinfo")
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=user.name, color=discord.Color.pink())
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="Joined", value=user.joined_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Created", value=user.created_at.strftime("%Y-%m-%d"), inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="serverinfo")
async def serverinfo(interaction: discord.Interaction):
    g = interaction.guild
    embed = discord.Embed(title=g.name, color=discord.Color.pink())
    embed.set_thumbnail(url=g.icon.url if g.icon else "")
    embed.add_field(name="Members", value=g.member_count, inline=True)
    embed.add_field(name="Boosts", value=g.premium_subscription_count, inline=True)
    await interaction.response.send_message(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))