from . import *
from .database.addwork_db import get_target_chat_with_data
from telethon.utils import get_peer_id


async def forward(e, task):
    if task.get("delay"):
        await asyncio.sleep(task["delay"])
    target_chats = task["target"]
    bl_words = task["blacklist_words"]
    head = True if task.get("show_forward_header") else False
    bl = True if task.get("has_to_blacklist") else False
    for chat in target_chats:
        try:
            if bl:
                if any((word.lower() in bl_words) for word in e.message.message.split()):
                    continue
            if head:
                await e.message.forward_to(chat)
            else:
                await e.client.send_message(chat, e.message)
        except BaseException:
            pass

@bot.on(events.NewMessage(incoming=True))
async def fwder(e):
    ch = await e.get_chat()
    chat_id = get_peer_id(ch)
    tasks = await get_target_chat_with_data(chat_id)
    for task in tasks:
        if task.get("has_to_forward"):
            await asyncio.ensure_future(forward(e, task))