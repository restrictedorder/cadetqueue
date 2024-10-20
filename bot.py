import discord
from discord.ext import commands, tasks
import asyncio
import datetime

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

cadet_queue = []
active_sessions = []
session_logs = {}

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

# Command to join the queue
@bot.command(name='joinqueue')
async def join_queue(ctx):
    member = ctx.author
    role = discord.utils.get(member.guild.roles, name="Cadet")
    if role in member.roles:
        if member not in cadet_queue:
            cadet_queue.append(member)
            await ctx.send(f'{member.display_name} has joined the queue.')
        else:
            await ctx.send(f'{member.display_name}, you are already in the queue.')
    else:
        await ctx.send('Only cadets can join the queue.')

# Command to leave the queue
@bot.command(name='leavequeue')
async def leave_queue(ctx):
    member = ctx.author
    if member in cadet_queue:
        cadet_queue.remove(member)
        await ctx.send(f'{member.display_name} has left the queue.')
    else:
        await ctx.send(f'{member.display_name}, you are not in the queue.')

# Command for FTOs to start a session
@bot.command(name='startsession')
async def start_session(ctx, cadet: discord.Member):
    member = ctx.author
    role = discord.utils.get(member.guild.roles, name="FTO")
    if role in member.roles:
        if cadet in cadet_queue:
            cadet_queue.remove(cadet)
            start_time = datetime.datetime.now()
            session_info = {'cadet': cadet, 'fto': member, 'start_time': start_time}
            active_sessions.append(session_info)
            await ctx.send(f'{cadet.display_name} has started a session with FTO {member.display_name}.')
        else:
            await ctx.send(f'{cadet.display_name} is not in the queue.')
    else:
        await ctx.send('Only FTOs can start sessions.')

# Command to end a session (FTO or Cadet can end it)
@bot.command(name='endsession')
async def end_session(ctx):
    member = ctx.author
    for session in active_sessions:
        if session['cadet'] == member or session['fto'] == member:
            end_time = datetime.datetime.now()
            duration = (end_time - session['start_time']).total_seconds() / 3600
            cadet_name = session['cadet'].display_name
            if cadet_name not in session_logs:
                session_logs[cadet_name] = 0
            session_logs[cadet_name] += duration
            active_sessions.remove(session)
            await ctx.send(f'Session with Cadet {session["cadet"].display_name} and FTO {session["fto"].display_name} has ended. Duration: {duration:.2f} hours.')
            return
    await ctx.send('You are not currently in an active session.')

# Command to view the current queue and active sessions
@bot.command(name='queue')
async def view_queue(ctx):
    queue_list = "\n".join([cadet.display_name for cadet in cadet_queue]) if cadet_queue else "No members currently in the queue."
    active_sessions_list = "\n".join([f"{session['cadet'].display_name} with FTO {session['fto'].display_name}" for session in active_sessions]) if active_sessions else "No active sessions."
    await ctx.send(f'**Cadet Queue:**\n{queue_list}\n\n**Active Sessions:**\n{active_sessions_list}')

# Command for admin options (only for Command role)
@bot.command(name='commandmenu')
async def command_menu(ctx):
    member = ctx.author
    role = discord.utils.get(member.guild.roles, name="Command")
    if role in member.roles:
        await ctx.send('**Admin Options:**\n1. !clearqueue - Clears the cadet queue.\n2. !clearsessions - Ends all active sessions.\n3. !movequeue <cadet> <position> - Move a cadet to a specific position in the queue.')
    else:
        await ctx.send('You do not have permission to use the command menu.')

# Command to clear the queue (admin only)
@bot.command(name='clearqueue')
async def clear_queue(ctx):
    member = ctx.author
    role = discord.utils.get(member.guild.roles, name="Command")
    if role in member.roles:
        cadet_queue.clear()
        await ctx.send('The cadet queue has been cleared.')
    else:
        await ctx.send('You do not have permission to clear the queue.')

# Command to clear active sessions (admin only)
@bot.command(name='clearsessions')
async def clear_sessions(ctx):
    member = ctx.author
    role = discord.utils.get(member.guild.roles, name="Command")
    if role in member.roles:
        active_sessions.clear()
        await ctx.send('All active sessions have been ended.')
    else:
        await ctx.send('You do not have permission to clear the sessions.')

# Command to move a cadet in the queue (admin only)
@bot.command(name='movequeue')
async def move_queue(ctx, cadet: discord.Member, position: int):
    member = ctx.author
    role = discord.utils.get(member.guild.roles, name="Command")
    if role in member.roles:
        if cadet in cadet_queue:
            cadet_queue.remove(cadet)
            cadet_queue.insert(position - 1, cadet)
            await ctx.send(f'{cadet.display_name} has been moved to position {position} in the queue.')
        else:
            await ctx.send(f'{cadet.display_name} is not in the queue.')
    else:
        await ctx.send('You do not have permission to move cadets in the queue.')

# Command to view session logs
@bot.command(name='sessionlogs')
async def view_session_logs(ctx):
    logs = "\n".join([f"{cadet}: {hours:.2f} hours" for cadet, hours in session_logs.items()]) if session_logs else "No session logs available."
    await ctx.send(f'**Session Logs:**\n{logs}')

# Run the bot
bot.run('YOUR_BOT_TOKEN')
