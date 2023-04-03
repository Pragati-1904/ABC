from . import *

HELP = """
/addtask - **To Add New Task**

/tasks - **To Manage And Edit Tasks**
"""

@bot.on(events.NewMessage(incoming=True, pattern="^/start$"))
async def _start(e):
    await e.reply("**Hello**", buttons=[[Button.inline("HELP ⛑️", data="hlp")]])

@bot.on(events.callbackquery.CallbackQuery(data=re.compile("hlp")))
async def _hlp(e):
    await e.edit(HELP)